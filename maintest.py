import sys
import prman, os

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
    ri.Option("searchpath", {"string archive": "./assets/:@"})
    ri.Option("searchpath", {"string texture": "./textures/:@"})
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
    
    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})
    ri.Translate(0.0, 1.0, 20.0)
    ri.Rotate(-30, 1,0,0)
    ri.Rotate(-180, 0, 1, 0) # Camera rotation x axis
    ri.WorldBegin()
    
    #######################################################################
    # LIGHTING SECTION
    #######################################################################
    
    # Light1.Environment Light
    ri.TransformBegin()
    ri.AttributeBegin()
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
    # ri.Translate(2, 8, -8)
    # ri.Rotate(45, 1, 0, 0) 
    # ri.Rotate(45, 0, 1, 0)
    # ri.Light("PxrRectLight", "Light0", {"float intensity": 100})
    # ri.AttributeEnd()
    # ri.TransformEnd()
    
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
    ri.Bxdf("PxrDiffuse", "grey", {"color diffuseColor": [0.5, 0.5, 0.5]})  # Darker grey for floor
    ri.TransformBegin()
    ri.Polygon({ri.P: [-20, 0, 20, 20, 0, 20, 20, 0, -20, -20, 0, -20]})
    ri.TransformEnd()
    ri.AttributeEnd()


    ################
    # Sphere 1
    ################
    
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    ## Fractal como patrón de ruido
    ri.Pattern("PxrDirt", "fractalNoise", {
        "float frequency": [10.0],
        "float amplitude": [10.0]
    })

    ri.Bxdf("PxrDisney", "stainlessSteelMaterial", {
        "color baseColor": [0.75, 0.75, 0.75],   # Color base (gris plateado)
        "float metallic": [1.0],                  # Es completamente metálico
        "float specular": [1.0],                  # Alta especularidad (reflejos brillantes)
        "float roughness": [0.1],                 # Baja rugosidad para un acabado pulido y brillante
    })
     
    ri.Translate(-12.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    ################
    # Sphere 2
    ################
    
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    ri.Pattern("metalz", "metalPattern1", {
        "float Ks": [0.5],
        "color Cs": [0.299, 0.312, 0.343],
        "float scale": [1.0],
        "float frequency" : [0.1]
    })

    ri.Bxdf("PxrDisney", "stainlessSteelMaterial", {
        "color baseColor": [0.75, 0.75, 0.75],   # Color base (gris plateado)
        "float metallic": [1.0],                  # Es completamente metálico
        "float specular": [1.0],                  # Alta especularidad (reflejos brillantes)
        "float roughness": [0.1],                 # Baja rugosidad para un acabado pulido y brillante
    })
    
    ri.Translate(-8.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    ################
    # Sphere 3
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()

    ri.Pattern("stainless_steel", "stainlessSteelPattern", {
        "color baseBar": [0.8, 0.0, 0.0],
        "float roughness": [0.8],
        "float reflectivity": [0.5]
    })

    ri.Bxdf("PxrSurface", "stainlessMaterial", {
        "reference color specularFaceColor": ["stainlessSteelPattern:Cout"],
        "float diffuseGain": [0.0],
        "float specularRoughness": [0.2]
    })

    ri.Translate(-4.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    ################
    # Sphere 4
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    ri.Bxdf("PxrDisney", "stainlessSteelMaterial", {
        "color baseColor": [0.75, 0.75, 0.75],   # Color base (gris plateado)
        "float metallic": [1.0],                  # Es completamente metálico
        "float specular": [1.0],                  # Alta especularidad (reflejos brillantes)
        "float roughness": [0.1],                 # Baja rugosidad para un acabado pulido y brillante
    })

    ri.Translate(0.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    ################
    # Sphere 5
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    # Very usefull for metalic surfaces 
    ri.Bxdf("PxrDisney", "goldMaterial", {
        "color baseColor": [0.93, 0.6, 0.06],         # Color base (para un metal dorado, por ejemplo)
        "float metallic": [1.0],                       # Define que el material es completamente metálico
        "float specular": [1.0],                       # Controla la intensidad de las reflexiones especulares
        "float roughness": [0.05],                     # Baja rugosidad para reflejos nítidos
    })

    ri.Translate(4.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    ################
    # Sphere 6  NOT AVAILABLE
    ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    
    # ri.Bxdf("PxrMetal", "metalColor2", {
    #     "color baseColor": [0.75, 0.75, 0.75],
    #     "float anisotropy": [0.2],  # Esto puede no ser compatible
    #     "float metallic": [1.0],
    #     "float ior": [2.0],
    #     "float specular": [1.0],
    #     "float roughness": [0.05]
    # })
    
    # ri.Translate(8.0, 2.0, 0.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
     
    ################
    # Sphere 7
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    ri.Bxdf("LamaConductor", "metalMaterial", {
        "color baseColor": [0.93, 0.6, 0.06],    # Color metálico
        "float roughness": [0.05],               # Baja rugosidad para reflejos nítidos
        "float IOR": [1.5],                      # Índice de refracción para el metal
        "float metallic": [1.0]                  # Para asegurar que el material sea metálico
    })
        
    ri.Translate(12.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
     
    ################
    # Sphere 8
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    ri.Translate(16.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    #  ################
    # # Sphere 9        pattern 
    # ################
    
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    ## Fractal como patrón de ruido
    ri.Pattern("PxrFractal", "fractalNoise", {
        "float frequency": [10.0],
        "float amplitude": [1.0]
    })

    # Usar ese patrón para modificar el color especular
    ri.Bxdf("PxrSurface", "metalSurface", {
        "reference color specularFaceColor": ["fractalNoise:resultRGB"],
        "float specularRoughness": [0.1]
    })

    ri.Translate(-12.0, 2.0, 4.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    # ################
    # # Sphere 10  # Displacemente quizas necesito definir la forma de la que quiero importarlo
    # ################
    
    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    
    # ri.Displacement("displaceShader", {
    #     "float amplitude": [0.1],
    #     "string textureFile": ["bumpTexture.exr"]
    # })

    # ri.Bxdf("PxrSurface", "metalSurface", {
    #     "color diffuseColor": [0.93, 0.6, 0.06],
    #     "color specularColor": [0.5, 1.0, 1.0],
    #     "float specularRoughness": [0.1]
    # })

    # ri.Translate(-8.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    ################
    # Sphere 11
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    # Aplicar desplazamiento en el shading
    ri.Attribute("displacementbound", {"sphere": 0.7, "coordinatesystem": "shader"})

    # PxrFractal para generar ruido
    ri.Pattern("PxrFractal", "fractalPattern", {
        "float frequency": [5.0],
        "float amplitude": [0.5]
    })

    # PxrBump usando el resultado de fractal
    ri.Pattern("PxrBump", "bumpPattern", {
        "reference float inputBump": ["fractalPattern:resultF"],
        "float bumpHeight": [0.01],
        "int bumpType": [0]
    })

    # PxrSurface usando bump
    ri.Bxdf("PxrSurface", "bumpyMaterial", {
        "color diffuseColor": [0.1, 0.1, 0.1],
        "reference normal bumpNormal": ["bumpPattern:resultN"]
    })

    ri.Translate(-4.0, 2.0, 4.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    # ################
    # # Sphere 12        "Best rubber shader for dumbbell weights"
    # ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    ri.Attribute("displacementbound", {"sphere": 0.1, "coordinatesystem": "shader"})

    # PxrFractal para generar ruido tipo grano fino
    ri.Pattern("PxrFractal", "fractalPattern", {
        "float frequency": [20.0],     # Alta frecuencia = más detalles pequeños
        "float amplitude": [0.3]       # Ajusta según el efecto deseado
    })

    # PxrBump utilizando el patrón como entrada
    ri.Pattern("PxrBump", "bumpPattern", {
        "reference float inputBump": ["fractalPattern:resultF"],
        "float bumpHeight": [0.05],    # Aumenta si quieres más relieve
        "int bumpType": [0]            # 0 = screen space
    })

    # Asignar el material con el bump aplicado
    ri.Bxdf("PxrSurface", "bumpyMaterial", {
        "color diffuseColor": [0.1, 0.1, 0.1],  # Goma negra o gris oscura
        "reference normal bumpNormal": ["bumpPattern:resultN"],
        "float specularFaceColor": [0.02],     # Muy poco brillo
        "float specularRoughness": [0.6]       # Alta rugosidad para aspecto mate
    })
    
    ri.Translate(0.0, 2.0, 4.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    ################
    # Sphere 13
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    
    ri.Pattern("PxrManifold2D", "cylindricalUV", {
        "int source": [1],  # 1 = cylindrical
        "float scaleS": [80.0],
        "float scaleT": [1.0]
    })

    ri.Pattern("PxrPhasorNoise", "revolutionlines", {
        "reference struct inputManifold": "cylindricalUV:result.Q",
        "float frequency": [7.0],
        "int layers": [1],
        "float pulseWidth": [0.8],
    })

    ri.Pattern("PxrBump", "revolutionbump", {
        "reference float inputBump": "revolutionlines:resultF",
        "float bumpHeight": [0.1]
    })

    ri.Bxdf("PxrDisney", "revolutionEffect", {
        "color baseColor": [0.75, 0.75, 0.75],
        "reference normal bumpNormal": "revolutionbump:resultN",
        "float metallic": [1.0],
        "float specular": [1.0],
        "float roughness": [0.02],
       
    })

    ri.Translate(4.0, 2.0, 4.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    # ################
    # # Sphere 14
    # ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()

    ri.Pattern("PxrManifold2D", "cylindricalUV", {
        "int source": [1],  # 1 = cylindrical mapping
        "float scaleS": [80.0],   # eje alrededor del objeto
        "float scaleT": [1.0],  # número de líneas concéntricas
    })

    # Patrón tipo checker (lo usamos como líneas)
    ri.Pattern("PxrChecker", "checkerPattern", {
        "reference struct manifold": "cylindricalUV:result",
        "color colorA": [0.8, 0.8, 0.8],  # color metálico claro
        "color colorB": [0.3, 0.3, 0.3],  # línea oscura
    })

    # Aplicar como bump para simular los surcos
    ri.Pattern("PxrBump", "lineBump", {
        "reference float inputBump": "linePattern:resultR",
        "float bumpHeight": [0.1],
    })

    # Material metálico con líneas concéntricas
    ri.Bxdf("PxrDisney", "revolutionEffect", {
        "reference color baseColor": "checkerPattern:resultRGB",
        "float metallic": [1.0],
        "float roughness": [0.05],
        "float specular": [1.0],
    })


    # # Aplicar material PxrDisney con el bump
    # ri.Bxdf("PxrDisney", "revolutionEffect", {
    #     "color baseColor": [0.8, 0.8, 0.2],
    #     "reference normal bumpNormal": "checkerBump:resultN",  # << DEBE MATCHEAR
    #     "float metallic": [1.0],
    #     "float specular": [1.0],
    #     "float roughness": [0.02],
    # })

    ri.Translate(8.0, 2.0, 4.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)

    ri.TransformEnd()
    ri.AttributeEnd()

        
    # ################
    # # Sphere 15
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(12.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
     
    # ################
    # # Sphere 16
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(16.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    #  ################
    # # Sphere 17
    # ################
    
    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(-12.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 18
    # ################
    
    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(-8.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 19
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(-4.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    # ################
    # # Sphere 20
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(0.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 21
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(4.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 22
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(8.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
     
    # ################
    # # Sphere 23
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(12.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
     
    # ################
    # # Sphere 24
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(16.0, 2.0, 8.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()


    ri.WorldEnd()
    ri.End()

if __name__ == "__main__":

    # cl.checkAndCompileShader("shaders/neoprene")
    # cl.checkAndCompileShader("shaders/stainless_steel")
    # cl.checkAndCompileShader("shaders/rubber")
    # cl.checkAndCompileShader("shaders/rubber2")
    # cl.checkAndCompileShader("shaders/EdgeWearShader")
    # cl.checkAndCompileShader("shaders/ScratchShader")
    # cl.checkAndCompileShader("shaders/combinedShader")
    # cl.checkAndCompileShader("shaders/gold")

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
