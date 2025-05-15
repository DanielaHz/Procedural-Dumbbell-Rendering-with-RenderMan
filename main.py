# import the python functions
import sys
import prman
import argparse

sys.path.append("./common")
import ProcessCommandLine as cl

# Main rendering routine
def main(
    filename="dumbbell.rib",
    shadingrate=0.5,
    pixelvar=0.01,
    fov=73.0,
    width=1024,
    height=720,
    integrator="PxrPathTracer",
    integratorParams={},
):
    ########################################################################
    # RENDERMAN SETUP SECTION
    ########################################################################
    
    print("shading rate {} pixel variance {} using {} {}".format(shadingrate, pixelvar, integrator, integratorParams))
    ri = prman.Ri()  

    ri.Begin(filename)
    ri.Display("neoprene_shader.exr", "file", "rgba")
    ri.Option("searchpath", {"string archive": "./assets/:@"}) #search in assets folder
    ri.Option("searchpath", {"string texture": "./textures/:@"}) #search in textures folder
    ri.Option("searchpath", {"string shader": "./postshaders/:@"}) #search in postshaders folder for compiled shaders

    ri.Display("rgb.exr", "it", "rgba")
    ri.Format(width, height, 1)

    ri.Hider("raytrace", {"int incremental": [1]})
    ri.ShadingRate(shadingrate)
    ri.PixelVariance(pixelvar)
    ri.Integrator(integrator, 'integrator', integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})

    #######################################################################
    # CAMERA SETUP
    #######################################################################
    
    # Configuración de la cámara
    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})

    ri.Translate(0.5, -0.7, 8.0)
    ri.Rotate(-32, 1, 0, 0)
    ri.Rotate(-17, 0, 1, 0)
    ri.Rotate(180, 0, 1, 0)  # Gira la cámara 180 grados alrededor del eje Y

    # World Begin para los objetos de la escena
    ri.WorldBegin()

    #######################################################################
    # LIGHTING SECTION
    #######################################################################
    
    # Light1.Environment Light
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Rotate(250, 0, 1, 0)
    ri.Declare("domeLight", "string")
    ri.Attribute("visibility", {"int indirect": [1], "int transmission": [1], "int camera": [0]})
    ri.Light("PxrDomeLight", "domeLight", {
        "string lightColorMap": "gym_01_4k.tex",
        "float exposure": [0.5] 
    })
    ri.AttributeEnd()
    ri.TransformEnd()
    
    # Light2. Key Light    
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("Light0", "string")
    ri.Translate(0, 8, -5)
    ri.Rotate(90, 0, 0, 1) 
    ri.Rotate(-90, 0, 1, 0)
    ri.Light("PxrRectLight", "Light0", {"float intensity": 50})
    ri.AttributeEnd()
    ri.TransformEnd()
    
    # Light3. Fill Light
    # ri.TransformBegin()
    # ri.AttributeBegin()
    # ri.Declare("Light1", "string")
    # ri.Attribute("visibility", {"int camera": 0, "int transmission": 0})
    # ri.Translate(-3, 5, -5)        # Izquierda, un poco más baja, algo al frente
    # ri.Rotate(30, 1, 0, 0)         # Apunta ligeramente hacia abajo
    # ri.Rotate(-30, 0, 1, 0)        # Gira hacia el sujeto
    # ri.Light("PxrRectLight", "Light1", {"float intensity": 35})
    # ri.AttributeEnd()
    # ri.TransformEnd()

    # # Light4. Back Light
    # ri.TransformBegin()
    # ri.AttributeBegin()
    # ri.Declare("Light2", "string")
    # ri.Attribute("visibility", {"int camera": 0, "int transmission": 0}) # dont show the light in the final render
    # ri.Translate(6, 3, 0)  # Detrás del sujeto
    # ri.Rotate (270, 0, 1, 0)
    # ri.Light("PxrRectLight", "Light2", {"float intensity":25})
    # ri.AttributeEnd()
    # ri.TransformEnd()

    #######################################################################
    # MODEL SECTION
    #######################################################################

    #########
    # FLOOR
    #########
    
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "floor"})
    ri.Bxdf("PxrDiffuse", "grey", {"color diffuseColor": [0.6, 0.6, 0.6]})  # Darker grey for floor
    ri.TransformBegin()
    ri.Polygon({ri.P: [-50, 0, 50, 50, 0, 50, 50, 0, -50, -50, 0, -50]})
    ri.TransformEnd()
    ri.AttributeEnd()

    ################
    # DUMBBELL BAR
    ################
    
    ri.AttributeBegin()
    
    # Metalic base for the model
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()

    ri.Pattern("metalz", "metalPattern1", {
        "float Ks": [0.5],
        "color Cs": [0.8, 0.8, 0.8],
        "float scale": [1.0],          
        "float frequency": [1.0]  
    })

    ri.Bxdf("PxrSurface", "metalBxdf", {
        "reference color specularFaceColor": ["metalPattern1:resultColor"],
        "float diffuseGain": [0.0], 
        "float specularRoughness": [0.2]  
    })
    
    ri.ReadArchive("dum-center.rib")
    ri.TransformEnd()
    ri.AttributeEnd()
    
    ########################
    # DUMBBELL LEFT WEIGHT
    ########################
    
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell-left"})
    ri.TransformBegin()
    ri.Translate(-10, 0, 0)
    ri.Rotate(0, 1, 0, 0)

    # Rubber shader for left dumbbell
    ri.Bxdf("PxrDiffuse", "rubberMaterial", {
        "color diffuseColor": [0.06, 0.06, 0.06],  # Color base (en este caso rojo)
    })
    ri.ReadArchive("dum-left.rib")
    ri.TransformEnd()
    ri.AttributeEnd()

    #########################
    # DUMBBELL RIGHT WEIGHT
    #########################
    
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell-right"})
    ri.TransformBegin()
    ri.Translate(0.0, 0.0, 0.0)
    ri.Rotate(0, 0, 1, 0)

    ri.Bxdf("PxrDiffuse", "rubberMaterial", {
        "color diffuseColor": [0.06, 0.06, 0.06],  # Color base (en este caso rojo)
    })

    ri.ReadArchive("dum-right.rib")
    ri.TransformEnd()
    ri.AttributeEnd()

    ri.WorldEnd()
    ri.End()

if __name__ == "__main__":

    cl.checkAndCompileShader("shaders/metal")
  
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
