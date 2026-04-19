package
{
   import flash.display.MovieClip;
   import flash.events.Event;
   import flash.geom.Point;
   
   public class SSF2CharacterExt extends SSF2Character
   {
      private var effects:Array = new Array();
      
      private var clearListener:Boolean;
      
      private var _animationLock:String;
      
      private var _xOffset:*;
      
      private var _yOffset:*;
      
      private var _function:*;
      
      private var _receiver:*;
      
      private var _receiverType:*;
      
      private var _kb:*;
      
      private var _angle:*;
      
      private var _xDis:*;
      
      private var _yDis:*;
      
      private var _distance:*;
      
      private var _power:*;
      
      private var _maxPower:*;
      
      private var _kbc:* = 0;
      
      private var _wkb:* = 100;
      
      private var _tempData:Object;
      
      public function SSF2CharacterExt(param1:*)
      {
         super(param1);
      }
      
      public function flipX(param1:Number) : Number
      {
         if(this.isFacingRight())
         {
            return param1;
         }
         return param1 * -1;
      }
      
      private function jumpToContinue(param1:* = null) : *
      {
         this.removeEventListener(SSF2Event.GROUND_TOUCH,this.jumpToContinue);
         this.updateAttackStats({
            "allowControl":false,
            "cancelWhenAirborne":true
         });
         this.stancePlayFrame("continue");
      }
      
      public function setLandingLag(param1:Boolean) : void
      {
         if(param1)
         {
            this.removeEventListener(SSF2Event.GROUND_TOUCH,this.toLand);
            this.addEventListener(SSF2Event.GROUND_TOUCH,this.jumpToContinue);
            if(this.isOnGround())
            {
               this.jumpToContinue();
            }
         }
         else
         {
            this.removeEventListener(SSF2Event.GROUND_TOUCH,this.jumpToContinue);
            this.addEventListener(SSF2Event.GROUND_TOUCH,this.toLand);
            if(this.isOnGround())
            {
               this.toLand();
            }
         }
      }
      
      public function clearEffectsOnStateChange(param1:Boolean = true) : *
      {
         this.clearListener = param1;
         this.addEventListener(SSF2Event.STATE_CHANGE,this.removeAllEffects);
      }
      
      public function pushEffectBehind(param1:MovieClip) : *
      {
         SSF2API.getStage().getMidground().swapChildren(this.getMC(),param1);
         return param1;
      }
      
      public function addEffectToList(param1:MovieClip) : *
      {
         if(param1 != null)
         {
            this.effects.push(param1);
            return param1;
         }
         SSF2API.print("Tried to add a NULL effect to list!");
         return null;
      }
      
      public function removeAllEffects(param1:* = null) : *
      {
         var _loc2_:* = 0;
         while(_loc2_ < this.effects.length)
         {
            if(this.effects[_loc2_] != null)
            {
               if(this.effects[_loc2_].parent != null)
               {
                  this.effects[_loc2_].parent.removeChild(this.effects[_loc2_]);
               }
            }
            _loc2_++;
         }
         this.effects = new Array();
         if(this.clearListener && this.hasEventListener(SSF2Event.STATE_CHANGE,this.removeAllEffects) || param1 != null)
         {
            this.removeEventListener(SSF2Event.STATE_CHANGE,this.removeAllEffects);
         }
      }
      
      public function stopListening() : *
      {
         this.clearListener = false;
         this.removeEventListener(SSF2Event.STATE_CHANGE,this.removeAllEffects);
      }
      
      public function applyPaletteToEffect(param1:MovieClip) : *
      {
         var costumeData:Object;
         var onEffectEnterFrame:Function = null;
         var effectMC:MovieClip = param1;
         applyPalette(effectMC);
         costumeData = getPaletteSwapData();
         onEffectEnterFrame = function(param1:Event):*
         {
            if(isDisposed() || param1 != null && !effectMC.parent)
            {
               effectMC.removeEventListener(Event.ENTER_FRAME,onEffectEnterFrame);
               return;
            }
            var _loc2_:Object = getPaletteSwapData();
            if(_loc2_)
            {
               SSF2Utils.replacePalette(effectMC,_loc2_.paletteSwap);
            }
         };
         onEffectEnterFrame(null);
         effectMC.addEventListener(Event.ENTER_FRAME,onEffectEnterFrame);
      }
      
      public function setupAutolinkAngle(param1:Point, param2:Function = null, param3:Number = 60) : *
      {
         this.stopAutolinkAngle();
         this._animationLock = this.getCurrentAnimation();
         this._xOffset = param1.x;
         this._yOffset = param1.y;
         this._function = param2;
         this._maxPower = param3;
         this.addEventListener(SSF2Event.ATTACK_HIT,this._moveOpp);
      }
      
      public function stopAutolinkAngle() : *
      {
         if(this.hasEventListener(SSF2Event.ATTACK_HIT,this._moveOpp))
         {
            this.removeEventListener(SSF2Event.ATTACK_HIT,this._moveOpp);
         }
      }
      
      public function updateAutolinkTarget(param1:Point) : *
      {
         if(this.getCurrentAnimation() == this._animationLock)
         {
            this._xOffset = param1.x;
            this._yOffset = param1.y;
         }
      }
      
      public function updateAutolinkFunction(param1:Function) : *
      {
         if(this.getCurrentAnimation() == this._animationLock)
         {
            this._function = param1;
         }
      }
      
      private function _moveOpp(param1:* = null) : *
      {
         if(this.getCurrentAnimation() != this._animationLock)
         {
            this.stopAutolinkAngle();
         }
         else
         {
            this._receiver = param1.data.receiver;
            this._receiverType = this._receiver.getType().slice(4);
            if(this._receiverType == "Character" && this._notArmoured(this._receiver) || this._receiverType == "Item" || this._receiverType == "Enemy" || this._receiverType == "Projectile")
            {
               if(Boolean(this._receiver.getGameObjectStat("canReceiveKnockback")) && Boolean(this._receiver.getGameObjectStat("canReceiveHits")))
               {
                  this._xDis = this.getX() + this.flipX(this._xOffset) + this.getXSpeed() * 2 - this._receiver.getX();
                  this._yDis = this.getY() + this.getYSpeed() * 2 - this._receiver.getY() + this._yOffset;
                  this._yDis = -this._yDis * this._receiver.getGameObjectStat("gravity");
                  this._distance = Math.sqrt(Math.pow(Math.abs(this._xDis),2) + Math.pow(Math.abs(this._yDis),2));
                  if(this._function != null)
                  {
                     this._tempData = {
                        "receiver":this._receiver,
                        "distance":this._distance,
                        "attackBoxData":param1.data.attackBoxData
                     };
                     this._tempData = this._function(this._tempData);
                     this._distance = this._tempData.distance;
                  }
                  this._power = 30 + this._distance * 0.8;
                  if(this._power > this._maxPower)
                  {
                     this._power = this._maxPower;
                  }
                  this._kb = SSF2API.calculateKnockback(this._kbc,this._power,this._wkb,param1.data.attackBoxData.damage,this._receiver.getDamage(),this._getWeight(),false);
                  this._angle = Math.atan2(this._yDis,this._xDis);
                  this._angle = this._angle * 180 / Math.PI;
                  this._receiver.resetKnockback();
                  this._receiver.applyKnockback(this._kb,this._angle);
                  this._receiver.forceHitStun(param1.data.attackBoxData.hitStun);
               }
            }
         }
      }
      
      private function _getWeight() : Number
      {
         if(this._receiverType != "Projectile")
         {
            return this._receiver.getGameObjectStat("weight1");
         }
         return 100;
      }
      
      private function _notArmoured(param1:*) : Boolean
      {
         if(param1.getState() == CState.INJURED || param1.getState() == CState.FLYING || param1.getState() == CState.CRASH_LAND || param1.getState() == CState.CRASH_GETUP)
         {
            return true;
         }
         return false;
      }
   }
}

