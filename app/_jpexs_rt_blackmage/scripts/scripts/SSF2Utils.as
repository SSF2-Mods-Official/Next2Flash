package
{
   import fl.motion.*;
   import flash.display.*;
   import flash.filters.*;
   import flash.geom.*;
   import flash.utils.*;
   
   public class SSF2Utils
   {
      private static var paletteRect:Rectangle = new Rectangle();
      
      private static var palettePoint:Point = new Point();
      
      public function SSF2Utils()
      {
         super();
      }
      
      public static function toRadians(param1:Number) : Number
      {
         return param1 * (3.14159265358979 / 180);
      }
      
      public static function toDegrees(param1:Number) : Number
      {
         return param1 * (180 / 3.14159265358979);
      }
      
      public static function getDistance(param1:Point, param2:Point) : Number
      {
         if(param1 == null || param2 == null)
         {
            return 0;
         }
         return Math.sqrt(Math.pow(param1.x - param2.x,2) + Math.pow(param1.y - param2.y,2));
      }
      
      public static function calculateXSpeed(param1:Number, param2:Number) : Number
      {
         return param1 * Math.cos(param2 * 3.14159265358979 / 180);
      }
      
      public static function calculateYSpeed(param1:Number, param2:Number) : Number
      {
         return param1 * Math.sin(param2 * 3.14159265358979 / 180);
      }
      
      public static function calculateSpeed(param1:Number, param2:Number) : Number
      {
         return Math.sqrt(Math.pow(param1,2) + Math.pow(param2,2));
      }
      
      public static function forceBase360(param1:Number) : Number
      {
         while(param1 < 0)
         {
            param1 += 360;
         }
         while(param1 >= 360)
         {
            param1 -= 360;
         }
         return param1;
      }
      
      public static function calculateDifferenceBetweenAngles(param1:Number, param2:Number) : Number
      {
         var _loc3_:Number = param2 - param1;
         while(_loc3_ < -180)
         {
            _loc3_ += 360;
         }
         while(_loc3_ > 180)
         {
            _loc3_ -= 360;
         }
         return _loc3_;
      }
      
      public static function getVelocityVector(param1:Number, param2:Number) : Point
      {
         var _loc3_:Point = new Point();
         _loc3_.x = param1 * Math.cos(param2 * 3.14159265358979 / 180);
         _loc3_.y = param1 * Math.sin(param2 * 3.14159265358979 / 180);
         return _loc3_;
      }
      
      public static function getAngleBetween(param1:Point, param2:Point) : Number
      {
         return SSF2Utils.forceBase360(Math.atan2(-(param2.y - param1.y),param2.x - param1.x) * 180 / 3.14159265358979);
      }
      
      public static function safeGotoAndStop(param1:MovieClip, param2:*) : void
      {
         var _loc3_:int = 0;
         if(param2 is int || param2 is Number)
         {
            if(param2 <= param1.totalFrames)
            {
               param1.gotoAndStop(param2);
            }
         }
         else if(param2 is String)
         {
            _loc3_ = 0;
            while(_loc3_ < param1.currentLabels.length)
            {
               if(param1.currentLabels[_loc3_].name == param2)
               {
                  param1.gotoAndStop(param2);
                  break;
               }
               _loc3_++;
            }
         }
      }
      
      public static function removeFrameScripts(param1:MovieClip) : void
      {
         var _loc2_:int = 0;
         _loc2_ = 0;
         while(_loc2_ < param1.totalFrames)
         {
            param1.addFrameScript(_loc2_,null);
            _loc2_++;
         }
      }
      
      public static function setTint(param1:DisplayObject, param2:Number, param3:Number, param4:Number, param5:Number, param6:Number, param7:Number, param8:Number, param9:Number) : void
      {
         var _loc10_:ColorTransform = new ColorTransform();
         _loc10_.redMultiplier = param2;
         _loc10_.greenMultiplier = param3;
         _loc10_.blueMultiplier = param4;
         _loc10_.alphaMultiplier = param5;
         _loc10_.redOffset = param6;
         _loc10_.greenOffset = param7;
         _loc10_.blueOffset = param8;
         _loc10_.alphaOffset = param9;
         param1.transform.colorTransform = _loc10_;
      }
      
      public static function rotateRectangleAroundOrigin(param1:Rectangle, param2:Number) : Rectangle
      {
         var _loc4_:Point = null;
         var _loc5_:Point = null;
         var _loc6_:Point = null;
         var _loc7_:Point = null;
         var _loc3_:Rectangle = param1.clone();
         var _loc8_:* = 0;
         var _loc9_:* = 0;
         var _loc10_:* = 0;
         var _loc11_:* = 0;
         var _loc12_:* = 0;
         var _loc13_:* = 0;
         var _loc14_:* = 0;
         var _loc15_:* = 0;
         var _loc16_:* = 0;
         var _loc17_:* = 0;
         var _loc18_:* = 0;
         var _loc19_:* = 0;
         if(param2 != 0)
         {
            _loc4_ = new Point(_loc3_.x,_loc3_.y);
            _loc5_ = new Point(_loc3_.x + _loc3_.width,_loc3_.y);
            _loc6_ = new Point(_loc3_.x + _loc3_.width,_loc3_.y + _loc3_.height);
            _loc7_ = new Point(_loc3_.x,_loc3_.y + _loc3_.height);
            _loc12_ = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(),_loc4_));
            _loc13_ = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(),_loc5_));
            _loc14_ = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(),_loc6_));
            _loc15_ = SSF2Utils.toRadians(SSF2Utils.getAngleBetween(new Point(),_loc7_));
            _loc16_ = Point.distance(new Point(),_loc4_);
            _loc17_ = Point.distance(new Point(),_loc5_);
            _loc18_ = Point.distance(new Point(),_loc6_);
            _loc19_ = Point.distance(new Point(),_loc7_);
            _loc4_ = Point.polar(_loc16_,_loc12_ + SSF2Utils.toRadians(param2));
            _loc5_ = Point.polar(_loc17_,_loc13_ + SSF2Utils.toRadians(param2));
            _loc6_ = Point.polar(_loc18_,_loc14_ + SSF2Utils.toRadians(param2));
            _loc7_ = Point.polar(_loc19_,_loc15_ + SSF2Utils.toRadians(param2));
            _loc4_.y *= -1;
            _loc5_.y *= -1;
            _loc6_.y *= -1;
            _loc7_.y *= -1;
            _loc8_ = Math.min(_loc4_.x,_loc5_.x,_loc6_.x,_loc7_.x);
            _loc9_ = Math.min(_loc4_.y,_loc5_.y,_loc6_.y,_loc7_.y);
            _loc10_ = Math.max(_loc4_.x,_loc5_.x,_loc6_.x,_loc7_.x);
            _loc11_ = Math.max(_loc4_.y,_loc5_.y,_loc6_.y,_loc7_.y);
            _loc3_.x = _loc8_;
            _loc3_.y = _loc9_;
            _loc3_.width = _loc10_ - _loc8_;
            _loc3_.height = _loc11_ - _loc9_;
         }
         return _loc3_;
      }
      
      public static function cast(param1:*, param2:Class = null) : *
      {
         var _loc4_:* = undefined;
         var _loc3_:* = null;
         if(!param1)
         {
            return null;
         }
         if(!param2 && (param1 is SSF2Character || param1 is SSF2Projectile || param1 is SSF2Item || param1 is SSF2Enemy || param1 is SSF2Stage || param1 is SSF2Platform || param1 is SSF2CollisionBoundary || param1 is SSF2Camera || param1 is SSF2GameTimer || param1 is SSF2Target))
         {
            return param1;
         }
         if(param2)
         {
            _loc3_ = new param2(param1.$ext.getAPI());
         }
         else
         {
            _loc4_ = param1.getType();
            if("SSF2Character" === _loc4_)
            {
               _loc3_ = new SSF2Character(param1.$ext.getAPI());
            }
         }
         return _loc3_;
      }
      
      private static function cloneObject(param1:Object) : Object
      {
         return JSON.parse(JSON.stringify(param1));
      }
      
      private static function getCostumeObject(param1:Object = null) : Object
      {
         var _loc3_:int = 0;
         var _loc5_:* = undefined;
         param1 = param1 ? SSF2Utils.cloneObject(param1) : {};
         var _loc2_:Object = {};
         _loc2_.hue = 0;
         _loc2_.saturation = 0;
         _loc2_.brightness = 0;
         _loc2_.contrast = 0;
         _loc2_.redMultiplier = 1;
         _loc2_.greenMultiplier = 1;
         _loc2_.blueMultiplier = 1;
         _loc2_.alphaMultiplier = 1;
         _loc2_.redOffset = 0;
         _loc2_.greenOffset = 0;
         _loc2_.blueOffset = 0;
         _loc2_.alphaOffset = 0;
         var _loc4_:* = _loc2_;
         while(hasnext2(_loc4_,_loc3_))
         {
            _loc5_ = nextname(_loc4_,_loc3_);
            if(param1[_loc5_] === undefined)
            {
               param1[_loc5_] = _loc2_[_loc5_];
            }
         }
         return param1;
      }
      
      public static function setColorFilters(param1:DisplayObject, param2:Object) : void
      {
         var _loc3_:* = null;
         var _loc4_:* = null;
         if(!param2)
         {
            param1.filters = null;
            return;
         }
         param2 = SSF2Utils.getCostumeObject(param2);
         var _loc5_:Array = [];
         if(param2.hue != 0 && param2.saturation == 0 && param2.brightness == 0 && param2.contrast == 0)
         {
            _loc3_ = new AdjustColor();
            _loc3_.hue = param2.hue || 0;
            _loc3_.saturation = param2.saturation || 0;
            _loc3_.brightness = param2.brightness || 0;
            _loc3_.contrast = param2.contrast || 0;
            _loc5_.push(new ColorMatrixFilter(_loc3_.CalculateFinalFlatArray()));
         }
         if(param2.redMultiplier != 1 && param2.greenMultiplier == 1 && param2.blueMultiplier == 1 && param2.alphaMultiplier == 1 && param2.redOffset == 0 && param2.greenOffset == 0 && param2.blueOffset == 0 && param2.alphaOffset == 0)
         {
            _loc4_ = [];
            _loc4_ = _loc4_.concat([param2.redMultiplier || 1,0,0,0,param2.redOffset || 0]);
            _loc4_ = _loc4_.concat([0,param2.greenMultiplier || 1,0,0,param2.greenOffset || 0]);
            _loc4_ = _loc4_.concat([0,0,param2.blueMultiplier || 1,0,param2.blueOffset || 0]);
            _loc4_ = _loc4_.concat([0,0,0,param2.alphaMultiplier || 1,param2.alphaOffset || 0]);
            _loc5_.push(new ColorMatrixFilter(_loc4_));
         }
         param1.filters = _loc5_;
      }
      
      public static function replacePalette(param1:MovieClip, param2:Object, param3:int = 1, param4:Boolean = false, param5:Boolean = false) : void
      {
         var _loc6_:int = 0;
         var _loc7_:* = null;
         if((param2 || param4) && Boolean(param1))
         {
            _loc6_ = 0;
            _loc7_ = null;
            _loc6_ = 0;
            while(_loc6_ < param1.numChildren)
            {
               if(param1.getChildAt(_loc6_) is Bitmap)
               {
                  _loc7_ = param1.getChildAt(_loc6_) as Bitmap;
                  if(param4)
                  {
                     if(!param1.__cachedPalette || !param1.__cachedPalette[_loc7_.bitmapData])
                     {
                        param1.__cachedPalette = param1.__cachedPalette || new Dictionary(true);
                        param1.__cachedPalette[_loc7_.bitmapData] = _loc7_.bitmapData.clone();
                     }
                     else
                     {
                        _loc7_.bitmapData.draw(param1.__cachedPalette[_loc7_.bitmapData]);
                     }
                  }
                  if(param2)
                  {
                     SSF2Utils.replacePaletteHelper(_loc7_.bitmapData,param2);
                  }
                  _loc7_.smoothing = param5;
               }
               else if(param1.getChildAt(_loc6_) is MovieClip && param3 > 0)
               {
                  SSF2Utils.replacePalette(param1.getChildAt(_loc6_) as MovieClip,param2,param3 - 1,param4,param5);
               }
               _loc6_++;
            }
         }
      }
      
      private static function replacePaletteHelper(param1:BitmapData, param2:Object) : void
      {
         var _loc3_:int = 0;
         paletteRect.width = param1.width;
         paletteRect.height = param1.height;
         _loc3_ = 0;
         while(_loc3_ < param2.colors.length)
         {
            if(param2.colors[_loc3_] != param2.replacements[_loc3_])
            {
               param1.threshold(param1,paletteRect,palettePoint,"==",param2.colors[_loc3_],param2.replacements[_loc3_],4294967295,true);
            }
            _loc3_++;
         }
      }
      
      public static function decel(param1:Number, param2:Number) : Number
      {
         var _loc3_:* = false;
         if(param1 == 0)
         {
            return 0;
         }
         if(param2 >= 0)
         {
            param1 *= param2;
         }
         else
         {
            _loc3_ = param1 > 0;
            param1 -= param1 > 0 ? Math.abs(param2) : -Math.abs(param2);
            if(_loc3_ && param1 < 0 || !_loc3_ && param1 > 0)
            {
               param1 = 0;
            }
         }
         if(Math.abs(param1) < 0.5)
         {
            param1 = 0;
         }
         return param1;
      }
      
      public static function setBrightness(param1:MovieClip, param2:Number) : void
      {
         if(Math.abs(param2) > 100)
         {
            param2 = param2 > 0 ? 100 : -100;
         }
         var _loc3_:ColorTransform = new ColorTransform();
         _loc3_.redOffset = param2 * 2.55;
         _loc3_.greenOffset = param2 * 2.55;
         _loc3_.blueOffset = param2 * 2.55;
         param1.transform.colorTransform = _loc3_;
      }
      
      public static function safeRemoveMC(param1:MovieClip) : void
      {
         if(param1.parent)
         {
            param1.parent.removeChild(param1);
         }
      }
      
      public static function getControlsAngle(param1:Object) : Number
      {
         if(param1.UP && !param1.DOWN && Boolean(param1.LEFT) && !param1.RIGHT)
         {
            return 135;
         }
         if(param1.UP && !param1.DOWN && !param1.LEFT && Boolean(param1.RIGHT))
         {
            return 45;
         }
         if(!param1.UP && param1.DOWN && Boolean(param1.LEFT) && !param1.RIGHT)
         {
            return 225;
         }
         if(!param1.UP && param1.DOWN && !param1.LEFT && Boolean(param1.RIGHT))
         {
            return 315;
         }
         if(param1.UP && !param1.DOWN && !param1.LEFT && !param1.RIGHT)
         {
            return 90;
         }
         if(!param1.UP && param1.DOWN && !param1.LEFT && !param1.RIGHT)
         {
            return 270;
         }
         if(!param1.UP && !param1.DOWN && param1.LEFT && !param1.RIGHT)
         {
            return 180;
         }
         if(!param1.UP && !param1.DOWN && !param1.LEFT && Boolean(param1.RIGHT))
         {
            return 0;
         }
         return -1;
      }
   }
}

