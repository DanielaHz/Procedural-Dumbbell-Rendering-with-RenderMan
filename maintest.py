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
    ri.Translate(0.0,-2.0, 10.0)
    ri.Rotate(-30, 1,0,0)
    ri.Rotate(-180, 0, 1, 0) # Camera rotation x axis
    ri.WorldBegin()
    
    #######################################################################
    # LIGHTING SECTION
    #######################################################################
    
    # Light1.Environment Light
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("domeLight", "string")
    ri.Attribute("visibility", {"int indirect": [1], "int transmission": [1], "int camera": [0]})
    ri.Light("PxrDomeLight", "domeLight", {
        "string lightColorMap": "courtyard_4k.tex",
        "float exposure": [0.5] 
    })
    ri.AttributeEnd()
    ri.TransformEnd()
    
    # Light2. Key Light    
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("Light0", "string")
    ri.Translate(2, 8, -8)
    ri.Rotate(45, 1, 0, 0) 
    ri.Rotate(45, 0, 1, 0)
    ri.Light("PxrRectLight", "Light0", {"float intensity": 100})
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

    # Light4. Back Light
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("Light2", "string")
    ri.Attribute("visibility", {"int camera": 0, "int transmission": 0}) # dont show the light in the final render
    ri.Translate(6, 3, 0)  # Detrás del sujeto
    ri.Rotate (270, 0, 1, 0)
    ri.Light("PxrRectLight", "Light2", {"float intensity":25})
    ri.AttributeEnd()
    ri.TransformEnd()

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
    
    ri.Pattern("metalPattern", "metalPattern1", {
        "float Ks": [0.5],
        "color Cs": [0.9, 0.9, 0.9],
        "float scale": [10.0],
        "float frequency" : [3.0]
    })

    ri.Bxdf("PxrSurface", "metalBxdf", {
        "reference color specularFaceColor": ["metalPattern1:resultColor"],
        "float specularModelType": [1]
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
        "float scale": [10.0],
        "float frequency" : [3.0]
    })

    ri.Bxdf("PxrSurface", "metalBxdf", {
        "reference color specularFaceColor": ["metalPattern1:resultColor"],
        "float specularModelType": [1]
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
        "color baseBar": [1.0, 0.0, 0.0],
        "float roughness": [0.8],
        "float reflectivity": [0.5]
    })

    # Aplicar el material al objeto
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
    ri.Translate(4.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
    
    
    ################
    # Sphere 6
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
    ri.Translate(8.0, 2.0, 0.0)
    ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    ri.TransformEnd()
    ri.AttributeEnd()
     
    ################
    # Sphere 7
    ################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "metal-object"})
    ri.TransformBegin()
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
    # # Sphere 9
    # ################
    
    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(-12.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 10
    # ################
    
    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(-8.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 11
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(-4.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    # ################
    # # Sphere 12
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(0.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 13
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(4.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
    
    
    # ################
    # # Sphere 14
    # ################

    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "metal-object"})
    # ri.TransformBegin()
    # ri.Translate(8.0, 2.0, 4.0)
    # ri.Sphere(1.0, -1.0, 1.0, 360.0)  
    # ri.TransformEnd()
    # ri.AttributeEnd()
     
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
    cl.checkAndCompileShader("shaders/metalGold")

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
