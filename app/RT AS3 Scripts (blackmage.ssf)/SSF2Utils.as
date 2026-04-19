// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Utils

package 
{
    import flash.geom.Rectangle;
    import flash.geom.Point;
    import flash.display.MovieClip;
    import flash.geom.ColorTransform;
    import flash.display.DisplayObject;
    import flash.display.BitmapData;
    import fl.motion.*;
    import flash.display.*;
    import flash.geom.*;
    import flash.filters.*;
    import flash.utils.*;

    public class SSF2Utils 
    {

        private static var paletteRect:Rectangle = new Rectangle();
        private static var palettePoint:Point = new Point();


        public static function toRadians(_arg_1:Number):Number
        {
            return (_arg_1 * (3.14159265358979 / 180));
        }

        public static function toDegrees(_arg_1:Number):Number
        {
            return (_arg_1 * (180 / 3.14159265358979));
        }

        public static function getDistance(_arg_1:Point, _arg_2:Point):Number
        {
            if (((_arg_1 == null) || (_arg_2 == null)))
            {
                return (0);
            };
            return (Math.sqrt((Math.pow((_arg_1.x - _arg_2.x), 2) + Math.pow((_arg_1.y - _arg_2.y), 2))));
        }

        public static function calculateXSpeed(_arg_1:Number, _arg_2:Number):Number
        {
            return (_arg_1 * Math.cos(((_arg_2 * 3.14159265358979) / 180)));
        }

        public static function calculateYSpeed(_arg_1:Number, _arg_2:Number):Number
        {
            return (_arg_1 * Math.sin(((_arg_2 * 3.14159265358979) / 180)));
        }

        public static function calculateSpeed(_arg_1:Number, _arg_2:Number):Number
        {
            return (Math.sqrt((Math.pow(_arg_1, 2) + Math.pow(_arg_2, 2))));
        }

        public static function forceBase360(_arg_1:Number):Number
        {
            while (_arg_1 < 0)
            {
                _arg_1 = (_arg_1 + 360);
            };
            while (_arg_1 >= 360)
            {
                _arg_1 = (_arg_1 - 360);
            };
            return (_arg_1);
        }

        public static function calculateDifferenceBetweenAngles(_arg_1:Number, _arg_2:Number):Number
        {
            var _local_3:Number = (_arg_2 - _arg_1);
            while (_local_3 < -180)
            {
                _local_3 = (_local_3 + 360);
            };
            while (_local_3 > 180)
            {
                _local_3 = (_local_3 - 360);
            };
            return (_local_3);
        }

        public static function getVelocityVector(_arg_1:Number, _arg_2:Number):Point
        {
            var _local_3:Point = new Point();
            _local_3.x = (_arg_1 * Math.cos(((_arg_2 * 3.14159265358979) / 180)));
            _local_3.y = (_arg_1 * Math.sin(((_arg_2 * 3.14159265358979) / 180)));
            return (_local_3);
        }

        public static function getAngleBetween(_arg_1:Point, _arg_2:Point):Number
        {
            return (SSF2Utils.forceBase360(((Math.atan2(-(_arg_2.y - _arg_1.y), (_arg_2.x - _arg_1.x)) * 180) / 3.14159265358979)));
        }

        public static function safeGotoAndStop(_arg_1:MovieClip, _arg_2:*):void
        {
            var _local_3:int;
            if (((_arg_2 is int) || (_arg_2 is Number)))
            {
                if ((_arg_2 <= _arg_1.totalFrames))
                {
                    _arg_1.gotoAndStop(_arg_2);
                };
            }
            else
            {
                if ((_arg_2 is String))
                {
                    _local_3 = 0;
                    while (_local_3 < _arg_1.currentLabels.length)
                    {
                        if ((_arg_1.currentLabels[_local_3].name == _arg_2))
                        {
                            _arg_1.gotoAndStop(_arg_2);
                            return;
                        };
                        _local_3++;
                    };
                };
            };
        }

        public static function removeFrameScripts(_arg_1:MovieClip):void
        {
            var _local_2:int;
            _local_2 = 0;
            while (_local_2 < _arg_1.totalFrames)
            {
                _arg_1.addFrameScript(_local_2, null);
                _local_2++;
            };
        }

        public static function setTint(_arg_1:DisplayObject, _arg_2:Number, _arg_3:Number, _arg_4:Number, _arg_5:Number, _arg_6:Number, _arg_7:Number, _arg_8:Number, _arg_9:Number):void
        {
            var _local_10:ColorTransform = new ColorTransform();
            _local_10.redMultiplier = _arg_2;
            _local_10.greenMultiplier = _arg_3;
            _local_10.blueMultiplier = _arg_4;
            _local_10.alphaMultiplier = _arg_5;
            _local_10.redOffset = _arg_6;
            _local_10.greenOffset = _arg_7;
            _local_10.blueOffset = _arg_8;
            _local_10.alphaOffset = _arg_9;
            _arg_1.transform.colorTransform = _local_10;
        }

        public static function rotateRectangleAroundOrigin(_arg_1:Rectangle, _arg_2:Number):Rectangle
        {
            var _local_4:Point;
            var _local_5:Point;
            var _local_6:Point;
            var _local_7:Point;
            var _local_3:Rectangle = _arg_1.clone();
            var _local_8:* = 0;
            var _local_9:* = 0;
            var _local_10:* = 0;
            var _local_11:* = 0;
            var _local_12:* = 0;
            var _local_13:* = 0;
            var _local_14:* = 0;
            var _local_15:* = 0;
            var _local_16:* = 0;
            var _local_17:* = 0;
            var _local_18:* = 0;
            var _local_19:* = 0;
            if (_arg_2 != 0)
            {
                _local_4 = new Point(_local_3.x, _local_3.y);
                _local_5 = new Point((_local_3.x + _local_3.width), _local_3.y);
                _local_6 = new Point((_local_3.x + _local_3.width), (_local_3.y + _local_3.height));
                _local_7 = new Point(_local_3.x, (_local_3.y + _local_3.height));
                _local_12 = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(), _local_4));
                _local_13 = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(), _local_5));
                _local_14 = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(), _local_6));
                _local_15 = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(), _local_7));
                _local_16 = Point.distance(new Point(), _local_4);
                _local_17 = Point.distance(new Point(), _local_5);
                _local_18 = Point.distance(new Point(), _local_6);
                _local_19 = Point.distance(new Point(), _local_7);
                _local_4 = Point.polar(_local_16, (_local_12 + SSF2Utils.toRadians(_arg_2)));
                _local_5 = Point.polar(_local_17, (_local_13 + SSF2Utils.toRadians(_arg_2)));
                _local_6 = Point.polar(_local_18, (_local_14 + SSF2Utils.toRadians(_arg_2)));
                _local_7 = Point.polar(_local_19, (_local_15 + SSF2Utils.toRadians(_arg_2)));
                _local_4.y = (_local_4.y * -1);
                _local_5.y = (_local_5.y * -1);
                _local_6.y = (_local_6.y * -1);
                _local_7.y = (_local_7.y * -1);
                _local_8 = Math.min(_local_4.x, _local_5.x, _local_6.x, _local_7.x);
                _local_9 = Math.min(_local_4.y, _local_5.y, _local_6.y, _local_7.y);
                _local_10 = Math.max(_local_4.x, _local_5.x, _local_6.x, _local_7.x);
                _local_11 = Math.max(_local_4.y, _local_5.y, _local_6.y, _local_7.y);
                _local_3.x = _local_8;
                _local_3.y = _local_9;
                _local_3.width = (_local_10 - _local_8);
                _local_3.height = (_local_11 - _local_9);
            };
            return (_local_3);
        }

        public static function cast(_arg_1:*, _arg_2:Class=null):*
        {
            var _local_4:*;
            var _local_3:* = null;
            if (!_arg_1)
            {
                return (null);
            };
            if (((!(_arg_2)) && ((((((((((_arg_1 is SSF2Character) || (_arg_1 is SSF2Projectile)) || (_arg_1 is SSF2Item)) || (_arg_1 is SSF2Enemy)) || (_arg_1 is SSF2Stage)) || (_arg_1 is SSF2Platform)) || (_arg_1 is SSF2CollisionBoundary)) || (_arg_1 is SSF2Camera)) || (_arg_1 is SSF2GameTimer)) || (_arg_1 is SSF2Target))))
            {
                return (_arg_1);
            };
            if (_arg_2)
            {
                _local_3 = new _arg_2(_arg_1.$ext.getAPI());
            }
            else
            {
                switch (_arg_1.getType())
                {
                    case "SSF2Character":
                        _local_3 = new SSF2Character(_arg_1.$ext.getAPI());
                };
            };
            return (_local_3);
        }

        private static function cloneObject(_arg_1:Object):Object
        {
            return (JSON.parse(JSON.stringify(_arg_1)));
        }

        private static function getCostumeObject(_arg_1:Object=null):Object
        {
            var _local_3:int;
            var _local_5:*;
            _arg_1 = ((_arg_1) ? SSF2Utils.cloneObject(_arg_1) : {});
            var _local_2:Object = {};
            _local_2.hue = 0;
            _local_2.saturation = 0;
            _local_2.brightness = 0;
            _local_2.contrast = 0;
            _local_2.redMultiplier = 1;
            _local_2.greenMultiplier = 1;
            _local_2.blueMultiplier = 1;
            _local_2.alphaMultiplier = 1;
            _local_2.redOffset = 0;
            _local_2.greenOffset = 0;
            _local_2.blueOffset = 0;
            _local_2.alphaOffset = 0;
            var _local_4:* = _local_2;
            while (hasnext2(_local_4, _local_3))
            {
                _local_5 = nextname(_local_4, _local_3);
                if ((_arg_1[_local_5] === undefined))
                {
                    _arg_1[_local_5] = _local_2[_local_5];
                };
            };
            return (_arg_1);
        }

        public static function setColorFilters(_arg_1:DisplayObject, _arg_2:Object):void
        {
            var _local_3:* = null;
            var _local_4:* = null;
            if (!_arg_2)
            {
                _arg_1.filters = null;
                return;
            };
            _arg_2 = SSF2Utils.getCostumeObject(_arg_2);
            var _local_5:Array = [];
            if (((((!(_arg_2.hue == 0)) && (_arg_2.saturation == 0)) && (_arg_2.brightness == 0)) && (_arg_2.contrast == 0)))
            {
                _local_3 = new AdjustColor();
                _local_3.hue = ((_arg_2.hue) || (0));
                _local_3.saturation = ((_arg_2.saturation) || (0));
                _local_3.brightness = ((_arg_2.brightness) || (0));
                _local_3.contrast = ((_arg_2.contrast) || (0));
                _local_5.push(new ColorMatrixFilter(_local_3.CalculateFinalFlatArray()));
            };
            if (((((((((!(_arg_2.redMultiplier == 1)) && (_arg_2.greenMultiplier == 1)) && (_arg_2.blueMultiplier == 1)) && (_arg_2.alphaMultiplier == 1)) && (_arg_2.redOffset == 0)) && (_arg_2.greenOffset == 0)) && (_arg_2.blueOffset == 0)) && (_arg_2.alphaOffset == 0)))
            {
                _local_4 = [];
                _local_4 = _local_4.concat([((_arg_2.redMultiplier) || (1)), 0, 0, 0, ((_arg_2.redOffset) || (0))]);
                _local_4 = _local_4.concat([0, ((_arg_2.greenMultiplier) || (1)), 0, 0, ((_arg_2.greenOffset) || (0))]);
                _local_4 = _local_4.concat([0, 0, ((_arg_2.blueMultiplier) || (1)), 0, ((_arg_2.blueOffset) || (0))]);
                _local_4 = _local_4.concat([0, 0, 0, ((_arg_2.alphaMultiplier) || (1)), ((_arg_2.alphaOffset) || (0))]);
                _local_5.push(new ColorMatrixFilter(_local_4));
            };
            _arg_1.filters = _local_5;
        }

        public static function replacePalette(_arg_1:MovieClip, _arg_2:Object, _arg_3:int=1, _arg_4:Boolean=false, _arg_5:Boolean=false):void
        {
            var _local_6:int;
            var _local_7:* = null;
            if ((((_arg_2) || (_arg_4)) && (_arg_1)))
            {
                _local_6 = 0;
                _local_7 = null;
                _local_6 = 0;
                while (_local_6 < _arg_1.numChildren)
                {
                    if ((_arg_1.getChildAt(_local_6) is Bitmap))
                    {
                        _local_7 = (_arg_1.getChildAt(_local_6) as Bitmap);
                        if (_arg_4)
                        {
                            if (((!(_arg_1.__cachedPalette)) || (!(_arg_1.__cachedPalette[_local_7.bitmapData]))))
                            {
                                _arg_1.__cachedPalette = ((_arg_1.__cachedPalette) || (new Dictionary(true)));
                                _arg_1.__cachedPalette[_local_7.bitmapData] = _local_7.bitmapData.clone();
                            }
                            else
                            {
                                _local_7.bitmapData.draw(_arg_1.__cachedPalette[_local_7.bitmapData]);
                            };
                        };
                        if (_arg_2)
                        {
                            SSF2Utils.replacePaletteHelper(_local_7.bitmapData, _arg_2);
                        };
                        _local_7.smoothing = _arg_5;
                    }
                    else
                    {
                        if (((_arg_1.getChildAt(_local_6) is MovieClip) && (_arg_3 > 0)))
                        {
                            SSF2Utils.replacePalette((_arg_1.getChildAt(_local_6) as MovieClip), _arg_2, (_arg_3 - 1), _arg_4, _arg_5);
                        };
                    };
                    _local_6++;
                };
            };
        }

        private static function replacePaletteHelper(_arg_1:BitmapData, _arg_2:Object):void
        {
            var _local_3:int;
            paletteRect.width = _arg_1.width;
            paletteRect.height = _arg_1.height;
            _local_3 = 0;
            while (_local_3 < _arg_2.colors.length)
            {
                if (_arg_2.colors[_local_3] != _arg_2.replacements[_local_3])
                {
                    _arg_1.threshold(_arg_1, paletteRect, palettePoint, "==", _arg_2.colors[_local_3], _arg_2.replacements[_local_3], 0xFFFFFFFF, true);
                };
                _local_3++;
            };
        }

        public static function decel(_arg_1:Number, _arg_2:Number):Number
        {
            var _local_3:Boolean;
            if ((_arg_1 == 0))
            {
                return (0);
            };
            if ((_arg_2 >= 0))
            {
                _arg_1 = (_arg_1 * _arg_2);
            }
            else
            {
                _local_3 = (_arg_1 > 0);
                _arg_1 = (_arg_1 - ((_arg_1 > 0) ? Math.abs(_arg_2) : -(Math.abs(_arg_2))));
                if ((((_local_3) && (_arg_1 < 0)) || ((!(_local_3)) && (_arg_1 > 0))))
                {
                    _arg_1 = 0;
                };
            };
            if ((Math.abs(_arg_1) < 0.5))
            {
                _arg_1 = 0;
            };
            return (_arg_1);
        }

        public static function setBrightness(_arg_1:MovieClip, _arg_2:Number):void
        {
            if ((Math.abs(_arg_2) > 100))
            {
                _arg_2 = ((_arg_2 > 0) ? 100 : -100);
            };
            var _local_3:ColorTransform = new ColorTransform();
            _local_3.redOffset = (_arg_2 * 2.55);
            _local_3.greenOffset = (_arg_2 * 2.55);
            _local_3.blueOffset = (_arg_2 * 2.55);
            _arg_1.transform.colorTransform = _local_3;
        }

        public static function safeRemoveMC(_arg_1:MovieClip):void
        {
            if (_arg_1.parent)
            {
                _arg_1.parent.removeChild(_arg_1);
            };
        }

        public static function getControlsAngle(_arg_1:Object):Number
        {
            if (((((_arg_1.UP) && (!(_arg_1.DOWN))) && (_arg_1.LEFT)) && (!(_arg_1.RIGHT))))
            {
                return (135);
            };
            if (((((_arg_1.UP) && (!(_arg_1.DOWN))) && (!(_arg_1.LEFT))) && (_arg_1.RIGHT)))
            {
                return (45);
            };
            if (((((!(_arg_1.UP)) && (_arg_1.DOWN)) && (_arg_1.LEFT)) && (!(_arg_1.RIGHT))))
            {
                return (225);
            };
            if (((((!(_arg_1.UP)) && (_arg_1.DOWN)) && (!(_arg_1.LEFT))) && (_arg_1.RIGHT)))
            {
                return (315);
            };
            if (((((_arg_1.UP) && (!(_arg_1.DOWN))) && (!(_arg_1.LEFT))) && (!(_arg_1.RIGHT))))
            {
                return (90);
            };
            if (((((!(_arg_1.UP)) && (_arg_1.DOWN)) && (!(_arg_1.LEFT))) && (!(_arg_1.RIGHT))))
            {
                return (270);
            };
            if (((((!(_arg_1.UP)) && (!(_arg_1.DOWN))) && (_arg_1.LEFT)) && (!(_arg_1.RIGHT))))
            {
                return (180);
            };
            if (((((!(_arg_1.UP)) && (!(_arg_1.DOWN))) && (!(_arg_1.LEFT))) && (_arg_1.RIGHT)))
            {
                return (0);
            };
            return (-1);
        }


    }
}//package 

