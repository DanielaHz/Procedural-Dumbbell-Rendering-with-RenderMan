import prman
import ProcessCommandLine as cl

# Main rendering routine
def main(
    filename="dumbbell.rib",
    shadingrate=10,
    pixelvar=0.1,
    fov=45.0,
    width=2000,
    height=2000,
    integrator="PxrPathTracer",
    integratorParams={},
):
    print("shading rate {} pivel variance {} using {} {}".format(shadingrate, pixelvar, integrator, integratorParams))
    ri = prman.Ri()  # create an instance of the RenderMan interface

    # this is the begining of the rib archive generation we can only
    # make RI calls after this function else we get a core dump
    ri.Begin(filename)
    ri.Option("searchpath", {"string archive": "./assets/:@"})

    # now we add the display element using the usual elements
    # FILENAME DISPLAY Type Output format
    ri.Display("rgb.exr", "it", "rgba")
    ri.Format(width, height, 1)

    # setup the raytrace / integrators
    ri.Hider("raytrace", {"int incremental": [1]})
    ri.ShadingRate(shadingrate)
    ri.PixelVariance(pixelvar)
    # ri.Integrator (integrator ,'integrator',integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})
    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})

    ri.Rotate(10 ,0, 0.0 , 0)
    ri.Translate(0.0, -2.0,9.0)

    # now we start our world
    ri.WorldBegin()
    #######################################################################
    # Lighting We need geo to emit light
    #######################################################################
    ri.LightSource("PxrRectLight", {"float intensity": 30, "color lightColor": [1, 0.9, 0.8], "float exposure": 2})
    ri.Translate(0, 5, 5)  # Position the light
    # no lights for this one!
    #######################################################################
    # end lighting
    #######################################################################

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "dumbbell"})
    ri.TransformBegin()
    ri.Translate(0.0,0.5, 0.5)
    ri.Bxdf("PxrDiffuse", "dumbbell_material", {"color diffuseColor": [0.6, 0.1, 0.5]})
    ri.ReadArchive("dumbell_rotation.rib")
    ri.TransformEnd()
    ri.AttributeEnd()

    # end our world
    ri.WorldEnd()
    # and finally end the rib file
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



# Its important to separate the parts of the object to process in renderman the parts with differente textures
# the angle of the model when is imported
# should I recerate the environment where the object I want to render is?