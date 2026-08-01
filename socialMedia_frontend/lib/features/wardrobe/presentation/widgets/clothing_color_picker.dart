import 'package:flutter/material.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';
import '../../domain/models/color_model.dart';

class ClothingColorPicker extends StatefulWidget {
  final SelectedColor? initialColor;
  final ValueChanged<SelectedColor> onColorSelected;

  const ClothingColorPicker({
    super.key,
    this.initialColor,
    required this.onColorSelected,
  });

  @override
  State<ClothingColorPicker> createState() => _ClothingColorPickerState();
}

class _ClothingColorPickerState extends State<ClothingColorPicker> {
  MainColor? _selectedMainColor;
  SubColor? _selectedSubColor;
  Color? _customColor;

  @override
  void initState() {
    super.initState();
    _initFromInitialColor();
  }

  @override
  void didUpdateWidget(ClothingColorPicker oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialColor != oldWidget.initialColor) {
      setState(() {
        _initFromInitialColor();
      });
    }
  }

  void _initFromInitialColor() {
    if (widget.initialColor != null) {
      final initial = widget.initialColor!;
      
      if (initial.parentCategoryId == 'ozel') {
        _customColor = _colorFromHex(initial.hexCode);
        _selectedMainColor = null;
        _selectedSubColor = null;
        return;
      }
      
      try {
        _selectedMainColor = clothingColors.firstWhere(
            (c) => c.id == initial.parentCategoryId);
        _customColor = null;
        
        if (_selectedMainColor != null && _selectedMainColor!.subColors.isNotEmpty) {
          try {
            _selectedSubColor = _selectedMainColor!.subColors.firstWhere(
                (sc) => sc.hex.toUpperCase() == initial.hexCode.toUpperCase());
          } catch (e) {
            _selectedSubColor = null;
          }
        } else {
          _selectedSubColor = null;
        }
      } catch (e) {
        // Not a standard main color category
      }
    } else {
      _selectedMainColor = null;
      _selectedSubColor = null;
      _customColor = null;
    }
  }

  Color _colorFromHex(String hexColor) {
    hexColor = hexColor.replaceAll('#', '');
    if (hexColor.length == 6) {
      hexColor = 'FF$hexColor';
    }
    try {
      return Color(int.parse('0x$hexColor'));
    } catch (e) {
      return Colors.transparent;
    }
  }

  void _handleMainColorTap(MainColor color) {
    setState(() {
      _selectedMainColor = color;
      _selectedSubColor = null; 
      _customColor = null;
    });

    widget.onColorSelected(SelectedColor(
      name: color.name,
      hexCode: color.primaryHex,
      parentCategoryId: color.id,
    ));
  }

  void _handleSubColorTap(SubColor subColor) {
    setState(() {
      _selectedSubColor = subColor;
    });
    widget.onColorSelected(SelectedColor(
      name: subColor.name,
      hexCode: subColor.hex,
      parentCategoryId: _selectedMainColor!.id,
    ));
  }

  Future<void> _openCustomColorPicker() async {
    Color pickerColor = _customColor ?? Theme.of(context).colorScheme.primary;

    await showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Theme.of(context).colorScheme.surface,
          title: Text(
            'Özel Renk Seç',
            style: TextStyle(
              color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
            ),
          ),
          content: SingleChildScrollView(
            child: ColorPicker(
              pickerColor: pickerColor,
              onColorChanged: (color) {
                pickerColor = color;
              },
              pickerAreaHeightPercent: 0.8,
              enableAlpha: false,
              displayThumbColor: true,
              paletteType: PaletteType.hsvWithHue,
              labelTypes: const [],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(
                'İptal',
                style: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey),
              ),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                setState(() {
                  _customColor = pickerColor;
                  _selectedMainColor = null;
                  _selectedSubColor = null;
                });
                widget.onColorSelected(SelectedColor(
                  name: 'Özel Renk',
                  hexCode: '#${pickerColor.value.toRadixString(16).substring(2).toUpperCase()}',
                  parentCategoryId: 'ozel',
                ));
              },
              child: Text(
                'Seç',
                style: TextStyle(color: Theme.of(context).colorScheme.primary),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildMainColorSwatch(MainColor color) {
    final isSelected = _selectedMainColor?.id == color.id;

    return GestureDetector(
      onTap: () => _handleMainColorTap(color),
      child: Container(
        margin: const EdgeInsets.only(right: 12.0),
        child: Column(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: color.isPattern ? null : _colorFromHex(color.primaryHex),
                gradient: color.isPattern
                    ? const SweepGradient(
                        colors: [Colors.red, Colors.yellow, Colors.green, Colors.blue, Colors.purple, Colors.red],
                      )
                    : null,
                border: Border.all(
                  color: isSelected ? Theme.of(context).colorScheme.primary : Colors.grey.shade700,
                  width: isSelected ? 3 : 1,
                ),
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: Theme.of(context).colorScheme.primary.withOpacity(0.4),
                          blurRadius: 8,
                          spreadRadius: 2,
                        )
                      ]
                    : null,
              ),
              child: isSelected
                  ? Icon(
                      Icons.check,
                      color: (color.id == 'beyaz' || color.id == 'sari' || color.id == 'bej') 
                          ? Colors.black 
                          : Colors.white,
                    )
                  : null,
            ),
            const SizedBox(height: 6),
            Text(
              color.name,
              style: TextStyle(
                fontSize: 12,
                color: isSelected 
                  ? (Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white)
                  : (Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey),
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
              textAlign: TextAlign.center,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          height: 85,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              ...clothingColors.map((color) => _buildMainColorSwatch(color)),
              GestureDetector(
                onTap: _openCustomColorPicker,
                child: Container(
                  margin: const EdgeInsets.only(right: 12.0, left: 4.0),
                  child: Column(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _customColor ?? Theme.of(context).colorScheme.surface,
                          border: Border.all(
                            color: _customColor != null ? Theme.of(context).colorScheme.primary : Colors.grey.shade700,
                            width: _customColor != null ? 3 : 1,
                          ),
                        ),
                        child: Icon(
                          Icons.color_lens_outlined,
                          color: _customColor != null 
                            ? (_customColor!.computeLuminance() > 0.5 ? Colors.black : Colors.white) 
                            : (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Özel',
                        style: TextStyle(
                          fontSize: 12,
                          color: _customColor != null 
                            ? (Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white)
                            : (Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        AnimatedSize(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          child: (_selectedMainColor != null && _selectedMainColor!.subColors.isNotEmpty)
              ? Padding(
                  padding: const EdgeInsets.only(top: 16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${_selectedMainColor!.name} Tonları:',
                        style: TextStyle(
                          color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8.0,
                        runSpacing: 8.0,
                        children: _selectedMainColor!.subColors.map((subColor) {
                          final isSelected = _selectedSubColor?.id == subColor.id;
                          final subColorValue = _colorFromHex(subColor.hex);
                          return FilterChip(
                            label: Text(
                              subColor.name,
                              style: TextStyle(
                                color: isSelected 
                                  ? Colors.white 
                                  : (Theme.of(context).textTheme.bodyMedium?.color ?? Colors.white),
                              ),
                            ),
                            selected: isSelected,
                            onSelected: (_) => _handleSubColorTap(subColor),
                            avatar: CircleAvatar(
                              backgroundColor: subColorValue,
                              radius: 12,
                              child: isSelected ? const Icon(Icons.check, size: 14, color: Colors.white) : null,
                            ),
                            selectedColor: Theme.of(context).colorScheme.primary,
                            checkmarkColor: Colors.white,
                            backgroundColor: Theme.of(context).colorScheme.surface,
                            side: BorderSide(
                              color: isSelected 
                                ? Theme.of(context).colorScheme.primary 
                                : Colors.grey.shade800,
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                )
              : const SizedBox.shrink(),
        ),
      ],
    );
  }
}
