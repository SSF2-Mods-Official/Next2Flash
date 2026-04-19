// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2CharacterExt

package 
{
    import flash.display.MovieClip;
    import flash.events.Event;
    import flash.geom.Point;
    import flash.events.*;

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

        public function SSF2CharacterExt(_arg_1:*):void
        {
            super(_arg_1);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.isFacingRight())
            {
                return (_arg_1);
            };
            return (_arg_1 * -1);
        }

        private function jumpToContinue(_arg_1:*=null):*
        {
            this.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.updateAttackStats({
                "allowControl":false,
                "cancelWhenAirborne":true
            });
            this.stancePlayFrame("continue");
        }

        public function setLandingLag(_arg_1:Boolean):void
        {
            if (_arg_1)
            {
                this.removeEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
                this.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
                if (this.isOnGround())
                {
                    this.jumpToContinue();
                };
            }
            else
            {
                this.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
                this.addEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
                if (this.isOnGround())
                {
                    this.toLand();
                };
            };
        }

        public function clearEffectsOnStateChange(_arg_1:Boolean=true):*
        {
            this.clearListener = _arg_1;
            this.addEventListener(SSF2Event.STATE_CHANGE, this.removeAllEffects);
        }

        public function pushEffectBehind(_arg_1:MovieClip):*
        {
            SSF2API.getStage().getMidground().swapChildren(this.getMC(), _arg_1);
            return (_arg_1);
        }

        public function addEffectToList(_arg_1:MovieClip):*
        {
            if (_arg_1 != null)
            {
                this.effects.push(_arg_1);
                return (_arg_1);
            };
            SSF2API.print("Tried to add a NULL effect to list!");
            return (null);
        }

        public function removeAllEffects(_arg_1:*=null):*
        {
            var _local_2:* = 0;
            while (_local_2 < this.effects.length)
            {
                if (this.effects[_local_2] != null)
                {
                    if (this.effects[_local_2].parent != null)
                    {
                        this.effects[_local_2].parent.removeChild(this.effects[_local_2]);
                    };
                };
                _local_2++;
            };
            this.effects = new Array();
            if ((((this.clearListener) && (this.hasEventListener(SSF2Event.STATE_CHANGE, this.removeAllEffects))) || (!(_arg_1 == null))))
            {
                this.removeEventListener(SSF2Event.STATE_CHANGE, this.removeAllEffects);
            };
        }

        public function stopListening():*
        {
            this.clearListener = false;
            this.removeEventListener(SSF2Event.STATE_CHANGE, this.removeAllEffects);
        }

        public function applyPaletteToEffect(effectMC:MovieClip):*
        {
            var onEffectEnterFrame:Function;
            applyPalette(effectMC);
            var costumeData:Object = getPaletteSwapData();
            onEffectEnterFrame = function (_arg_1:Event):*
            {
                if (((isDisposed()) || ((!(_arg_1 == null)) && (!(effectMC.parent)))))
                {
                    effectMC.removeEventListener(Event.ENTER_FRAME, onEffectEnterFrame);
                    return;
                };
                var _local_2:Object = getPaletteSwapData();
                if (_local_2)
                {
                    SSF2Utils.replacePalette(effectMC, _local_2.paletteSwap);
                };
            };
            (onEffectEnterFrame(null));
            effectMC.addEventListener(Event.ENTER_FRAME, onEffectEnterFrame);
        }

        public function setupAutolinkAngle(_arg_1:Point, _arg_2:Function=null, _arg_3:Number=60):*
        {
            this.stopAutolinkAngle();
            this._animationLock = this.getCurrentAnimation();
            this._xOffset = _arg_1.x;
            this._yOffset = _arg_1.y;
            this._function = _arg_2;
            this._maxPower = _arg_3;
            this.addEventListener(SSF2Event.ATTACK_HIT, this._moveOpp);
        }

        public function stopAutolinkAngle():*
        {
            if (this.hasEventListener(SSF2Event.ATTACK_HIT, this._moveOpp))
            {
                this.removeEventListener(SSF2Event.ATTACK_HIT, this._moveOpp);
            };
        }

        public function updateAutolinkTarget(_arg_1:Point):*
        {
            if (this.getCurrentAnimation() == this._animationLock)
            {
                this._xOffset = _arg_1.x;
                this._yOffset = _arg_1.y;
            };
        }

        public function updateAutolinkFunction(_arg_1:Function):*
        {
            if (this.getCurrentAnimation() == this._animationLock)
            {
                this._function = _arg_1;
            };
        }

        private function _moveOpp(_arg_1:*=null):*
        {
            if (this.getCurrentAnimation() != this._animationLock)
            {
                this.stopAutolinkAngle();
            }
            else
            {
                this._receiver = _arg_1.data.receiver;
                this._receiverType = this._receiver.getType().slice(4);
                if ((((((this._receiverType == "Character") && (this._notArmoured(this._receiver))) || (this._receiverType == "Item")) || (this._receiverType == "Enemy")) || (this._receiverType == "Projectile")))
                {
                    if (((this._receiver.getGameObjectStat("canReceiveKnockback")) && (this._receiver.getGameObjectStat("canReceiveHits"))))
                    {
                        this._xDis = (((this.getX() + this.flipX(this._xOffset)) + (this.getXSpeed() * 2)) - this._receiver.getX());
                        this._yDis = (((this.getY() + (this.getYSpeed() * 2)) - this._receiver.getY()) + this._yOffset);
                        this._yDis = (-(this._yDis) * this._receiver.getGameObjectStat("gravity"));
                        this._distance = Math.sqrt((Math.pow(Math.abs(this._xDis), 2) + Math.pow(Math.abs(this._yDis), 2)));
                        if (this._function != null)
                        {
                            this._tempData = {
                                "receiver":this._receiver,
                                "distance":this._distance,
                                "attackBoxData":_arg_1.data.attackBoxData
                            };
                            this._tempData = this._function(this._tempData);
                            this._distance = this._tempData.distance;
                        };
                        this._power = (30 + (this._distance * 0.8));
                        if (this._power > this._maxPower)
                        {
                            this._power = this._maxPower;
                        };
                        this._kb = SSF2API.calculateKnockback(this._kbc, this._power, this._wkb, _arg_1.data.attackBoxData.damage, this._receiver.getDamage(), this._getWeight(), false);
                        this._angle = Math.atan2(this._yDis, this._xDis);
                        this._angle = ((this._angle * 180) / Math.PI);
                        this._receiver.resetKnockback();
                        this._receiver.applyKnockback(this._kb, this._angle);
                        this._receiver.forceHitStun(_arg_1.data.attackBoxData.hitStun);
                    };
                };
            };
        }

        private function _getWeight():Number
        {
            if (this._receiverType != "Projectile")
            {
                return (this._receiver.getGameObjectStat("weight1"));
            };
            return (100);
        }

        private function _notArmoured(_arg_1:*):Boolean
        {
            if (((((_arg_1.getState() == CState.INJURED) || (_arg_1.getState() == CState.FLYING)) || (_arg_1.getState() == CState.CRASH_LAND)) || (_arg_1.getState() == CState.CRASH_GETUP)))
            {
                return (true);
            };
            return (false);
        }


    }
}//package 

