import sys

import prman, os
import ProcessCommandLine as cl

# Main rendering routine
def main(
    filename="dumbbell.rib",
    shadingrate=10,
    pixelvar=0.1,
    fov=48.0,
    width=1024,
    height=720,
    integrator="PxrPathTracer",
    integratorParams={},
):      
    print("shading rate {} pixel variance {} using {} {}".format(shadingrate, pixelvar, integrator, integratorParams))
    ri = prman.Ri()  # create an instance of the RenderMan interface

    ri.Begin(filename)
    ri.Display("neoprene_shader.exr", "file", "rgba")
    ri.Option("searchpath", {"string archive": "./assets/:@"})
    ri.Option("searchpath", {"string texture": "./textures/:@"})

    ri.Display("rgb.exr", "it", "rgba")
    ri.Format(width, height, 1)

    ri.Hider("raytrace", {"int incremental": [1]})
    ri.ShadingRate(shadingrate)
    ri.PixelVariance(pixelvar)
    ri.Integrator(integrator, 'integrator', integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})
    
    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})

    ri.Translate(2.5, -1.0, 4.5)
    ri.Rotate(-25, 0, 1, 0)
    
    ri.WorldBegin()
    #######################################################################
    # Lighting We need geo to emit light
    #######################################################################
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("domeLight", "string")
    ri.Rotate(-90, 1, 0, 0)
    ri.Rotate(100, 0, 0, 1)
    ri.Attribute("visibility", {"int indirect": [0], "int transmission": [0], "int camera": [0]})
    ri.Light("PxrDomeLight", "domeLight", {"string lightColorMap": "Luxo-Jr_4000x2000.tex"})
    ri.AttributeEnd()
    ri.TransformEnd()
    #######################################################################
    # end lighting
    #######################################################################

    # floor model
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "floor"})
    ri.Bxdf("PxrDiffuse", "smooth", {"color diffuseColor": [0.8, 0.8, 0.8]})
    ri.TransformBegin()
    ri.Translate(0.0, 1.0, 0.0)  # Ajusta la posición del suelo
    ri.Polygon({ri.P: [-10, -1, 10, 10, -1, 10, 10, -1, -10, -10, -1, -10]})
    ri.TransformEnd()
    ri.AttributeEnd()
    
    # Dumbbell bar
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell-bar"})
    ri.TransformBegin()
    ri.Translate(0.0, 0.0, 0.0) 
    ri.Rotate(0, 0, 1, 0)  
    ri.Pattern("stainless_steel", "stainless_steel", {})
    ri.Bxdf(
        "PxrSurface",
        "plastic",
        {
            "reference color diffuseColor": ["stainless_steel:Cout"],
        },
    )
    ri.ReadArchive("2.rib")
    ri.TransformEnd()
    ri.AttributeEnd()
     
    # Dumbbell right weight 
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell-left"})
    ri.TransformBegin()
    ri.Translate(0.0, 0.0, 0.0) 
    ri.Rotate(0, 0, 1, 0)  
    ri.Pattern("neoprene", "neoprene", {})
    ri.Bxdf(
        "PxrSurface",
        "plastic",
        {
            "reference color diffuseColor": ["neoprene:Cout"],
        },
    )
    ri.ReadArchive("3.rib")
    ri.TransformEnd()
    ri.AttributeEnd()
    
    # Dumbbell left weight 
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell-left"})
    ri.TransformBegin()
    ri.Translate(0.0, 0.0, 0.0) 
    ri.Rotate(0, 0, 1, 0)  
    ri.Pattern("neoprene", "neoprene", {})
    ri.Bxdf(
        "PxrSurface",
        "plastic",
        {
            "reference color diffuseColor": ["neoprene:Cout"],
        },
    )
    ri.ReadArchive("1.rib")
    ri.TransformEnd()
    ri.AttributeEnd()


    ri.WorldEnd()
    ri.End()

if __name__ == "__main__":

    cl.checkAndCompileShader("shaders/neoprene")
    cl.checkAndCompileShader("shaders/stainless_steel")
    cl.ProcessCommandLine("testScenes.rib")
    main(
        cl.filename,
        cl.args.shadingrate,
        cl.args.pixelvar,
        cl.args.fov,
        cl.args.width,
        cl.args.height,
        cl.integrator,
        cl.integratorParams,
    )
