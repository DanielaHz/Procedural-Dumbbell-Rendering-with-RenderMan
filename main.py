import prman
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
    print("shading rate {} pivel variance {} using {} {}".format(shadingrate, pixelvar, integrator, integratorParams))
    ri = prman.Ri()  # create an instance of the RenderMan interface

    ri.Begin(filename)
    ri.Option("searchpath", {"string archive": "./assets/:@"}) #looking for the model in the assets folder
    ri.Option("searchpath", {"string texture": "./textures/:@"}) # looking fro textures in the folder textures

    ri.Display("rgb.exr", "it", "rgba")
    ri.Format(width, height, 1)

    ri.Hider("raytrace", {"int incremental": [1]})
    ri.ShadingRate(shadingrate)
    ri.PixelVariance(pixelvar)
    ri.Integrator(integrator, 'integrator', integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})
    
    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})

    ri.Translate(0.5, -1.0, 10.0)
    ri.Rotate(50, 0, 1, 0)
    
    ri.WorldBegin()
    #######################################################################
    # Lighting We need geo to emit light
    #######################################################################
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("domeLight", "string")
    ri.Rotate(-90, 1, 0, 0)
    ri.Rotate(90, 0, 0, 1)
    ri.Attribute("visibility", {"int camera": [0]})
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
    
    # Dumbbell model 
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell"})
    ri.TransformBegin()
    ri.Translate(0.0, -0.5, 0.0) 
    ri.Rotate(10, 0, 1, 0)  
    ri.Bxdf("PxrDiffuse", "dumbbell_material", {"color diffuseColor": [0.6, 0.1, 0.5]})
    ri.ReadArchive("model5.rib")
    ri.TransformEnd()
    ri.AttributeEnd()
    
    ri.WorldEnd()
    ri.End()

if __name__ == "__main__":
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
