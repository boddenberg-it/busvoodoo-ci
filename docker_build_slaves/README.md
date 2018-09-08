BusVoodoo docker images used for build pipelines on https://jenkins.blobb.me.

The build.sh script will build all images and is also used to re-build latest images on jenkins slaves themselves weekly.

Moreover, one can use these images to build locally with a different distro. This can be achieved by following invocation after desired image is build:

```
docker run -it --rm=true \
        -v "$BUSVOODOO_REPO":/build \
        "$BUSVOODOO_IMAGE" \
        BUSVOODOO_HARDWARE_VERSION="$HARDWARE_VERSION" rake

$HARDWARE_VERSION = {0,1}
$BUSVOODOO_IMAGE = {busvoodoo:archlinux_build,...}
$BUSVOODOO_REPO = absolute path to checked out busvoodoo repo/branch
```


