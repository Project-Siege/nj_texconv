# TexConv Blender Addon

TexConv is a Blender addon that facilitates the conversion of images to DDS format using TexConv. It provides a user-friendly interface within Blender to convert and manage texture files efficiently.

## Features

- Convert images to DDS format using TexConv
- Fix mip maps for individual materials or textures within a folder
- Specify compression format for DDS conversion
- Seamlessly integrate with Blender's Material properties panel

## Installation

1. Download the TexConv addon ZIP file from the [releases page](https://github.com/your-username/TexConv/releases).
2. In Blender, go to `Edit > Preferences > Add-ons`.
3. Click `Install...` and select the downloaded ZIP file.
4. Enable the TexConv addon by ticking the checkbox next to it.

## Usage

### Convert to DDS

1. Select the object with the material containing the texture you want to convert.
2. Go to the `Properties` panel, then navigate to the `Material` tab and find the `TexConv` panel.
3. Choose the desired compression format from the dropdown menu.
4. Click the `Convert` button to convert the texture to DDS format.

### Fix Mip Maps

1. Follow steps 1 and 2 from the "Convert to DDS" section.
2. Click the `Fix Mip Maps` button to fix mip maps for the selected material.

### Fix Folder Mip Maps

1. Locate the folder containing the textures you want to process.
2. Go to the `Properties` panel, then navigate to the `Material` tab and find the `TexConv` panel.
3. Click the `Fix Folder Mip Maps` button to fix mip maps for all DDS textures in the selected folder.

## Credits

This addon was developed by [Nomadic Jester](https://github.com/your-username).

## License

This addon is licensed under the [MIT License](LICENSE).
