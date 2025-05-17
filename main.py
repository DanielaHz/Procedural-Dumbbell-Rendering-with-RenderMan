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
    fov=48.0,
    width=1024,
    height=720,
    integrator="maxIndirectBounces",
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
    # ri.Rotate(30, 1, 0, 0)
    # ri.Rotate(0, 0, 1, 0)
    # ri.Declare("domeLight", "string")
    # ri.Attribute("visibility", {"int indirect": [1], "int transmission": [1], "int camera": [0]})
    # ri.Light("PxrDomeLight", "domeLight", {
    #     "string lightColorMap": "small_empty_room_3_4k.tex",
    #     "float exposure": [0.2]
    # })

    ri.Rotate(0, 0, 1, 0)
    ri.Declare("domeLight", "string")
    ri.Attribute("visibility", {"int indirect": [1], "int transmission": [1], "int camera": [0]})
    ri.Light("PxrDomeLight", "domeLight", {
        "string lightColorMap": "peppermint_powerplant_2_4k.tex",
        "float exposure": [0.1]
    })
    
    ri.AttributeEnd()
    ri.TransformEnd()

    # # Light2. Key Light
    # ri.TransformBegin()
    # ri.AttributeBegin()
    # ri.Declare("Light0", "string")
    # ri.Translate(2, 8, -5)
    # ri.Rotate(90, 0, 0, 1)
    # ri.Rotate(-90, 0, 1, 0)
    # ri.Light("PxrRectLight", "Light0", {"float intensity": 100})
    # ri.AttributeEnd()
    # ri.TransformEnd()

    # # Light3. Fill Light
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

    ri.Bxdf("PxrSurface", "grey", {"color diffuseColor": [0.05, 0.1, 0.3]})  # Darker grey for floor
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
    
    ri.Pattern("PxrManifold2D", "cylindricalUV", {
        "int source": [1],  # 1 = cylindrical mapping
        "float scaleS": [1.0],   # eje alrededor del objeto
        "float scaleT": [550.0],  # número de líneas concéntricas
    })

    # Patrón tipo checker (lo usamos como líneas)
    ri.Pattern("PxrChecker", "checkerPattern", {
        "reference struct manifold": "cylindricalUV:result",
        "color colorA": [0.75, 0.75, 0.75],  # color metálico claro
        "color colorB": [1.0, 1.0, 1.0],  # línea oscura
    })

    # Aplicar como bump para simular los surcos
    ri.Pattern("PxrBump", "lineBump", {
        "reference float inputBump": "linePattern:resultR",
        "float bumpHeight": [10.0],
    })

    # Material metálico con líneas concéntricas
    ri.Bxdf("PxrDisney", "revolutionEffect", {
        "reference color baseColor": "checkerPattern:resultRGB",
        "float metallic": [1.0],
        "float roughness": [0.05],
        "float specular": [1.0],
    })
    
    ri.ReadArchive("dum-center.rib")
    ri.TransformEnd()
    ri.AttributeEnd()

    #######################
    # DUMBBELL LEFT WEIGHT # improve the uv in this model
    #######################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell-left"})
    ri.TransformBegin()
    ri.Translate(-10, 0, 0)
    ri.Rotate(0, 1, 0, 0)
    
    ri.Attribute("displacementbound", {"sphere": 0.1, "coordinatesystem": "shader"})

    # PxrFractal para generar ruido tipo grano fino
    ri.Pattern("PxrFractal", "fractalPattern", {
        "float frequency": [60.0],     # Alta frecuencia = más detalles pequeños
        "float amplitude": [20.0]       # Ajusta según el efecto deseado
    })

    # PxrBump utilizando el patrón como entrada
    ri.Pattern("PxrBump", "bumpPattern", {
        "reference float inputBump": ["fractalPattern:resultF"],
        "float bumpHeight": [0.01],    # Aumenta si quieres más relieve
        "int bumpType": [1]            # 0 = screen space
    })

    ri.Bxdf("PxrSurface", "bumpyMaterial", {
        "color diffuseColor": [0.05, 0.05, 0.05],  # black rubber
        "reference normal bumpNormal": ["bumpPattern:resultN"],
        "float specularFaceColor": [0.1],     # Muy poco brillo
        "float specularRoughness": [0.4]       # Alta rugosidad para aspecto mate
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
        "color diffuseColor": [0.058, 0.060, 0.074],  
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
