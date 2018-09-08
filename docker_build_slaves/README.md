Script will re-build all BusVoodoo docker images used for build pipelines on https://jenkins.blobb.me.

Morover, one can use these images to build locally with a different distro. This can be achieved by following invocation after desired image is build:

```
docker run -it --rm=true \
        -v "$BUSVOODOO_REPO":/build \
        "$BUSVOODOO_IMAGE" \
        BUSVOODOO_HARDWARE_VERSION="$HARDWARE_VERSION" rake

$HARDWARE_VERSION = {0,1}
$BUSVOODOO_IMAGE = {busvoodoo:archlinux_build,...}
$BUSVOODOO_REPO = path to checked out busvoodoo repo/branch
```


