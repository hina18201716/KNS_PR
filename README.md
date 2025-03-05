<<<<<<< HEAD
# RAPTOR Docker Container

Run the following:

    docker build -t raptor .

to build the `raptor` container.
Use

    docker run -v .:/RAPTOR-NkS/SgrA-test/data -it --rm raptor

to run the container.

For cross-platform build, run

    docker buildx build --platform=linux/amd64,linux/arm64 -t raptor .
=======
# NkS_shadow

This is an repository to store all test Naked Singularity shadow images and its pipeline based on GRMHD simulated data. 
>>>>>>> e11689beab45fcacea96df2d36e4b00f36e69715
