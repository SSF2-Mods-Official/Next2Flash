package
{
    import flash.display.MovieClip;

    public class DeeSpearExt extends SSF2Projectile
    {

        public function DeeSpearExt(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function initialize():void
        {
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function followUser(_arg_1:Boolean, _arg_2:MovieClip, _arg_3:Boolean=false):void
        {
            var xOffset:* = undefined;
            var yOffset:* = undefined;
            var updatePos:Function;
            var following:Boolean = _arg_1;
            var effectMC:MovieClip = _arg_2;
            var persistent:Boolean = _arg_3;
            updatePos = function ():void
            {
                effectMC.x = (getX() + xOffset);
                effectMC.y = (getY() + yOffset);
            };
            xOffset = (effectMC.x - getX());
            yOffset = (effectMC.y - getY());
            var options:Object = {"hitStunPause":false};
            if (persistent)
            {
                options = {
                    "persistent":true,
                    "hitStunPause":false
                };
            }
            else
            {
                options = {
                    "persistent":false,
                    "hitStunPause":false
                };
            };
            if (following)
            {
                this.createTimer(1, 0, updatePos, options);
            }
            else
            {
                this.destroyTimer(updatePos);
            };
        }

        public function loopEffect(_arg_1:Boolean, _arg_2:MovieClip, _arg_3:Boolean=false):void
        {
            var doLoop:Function;
            var looping:Boolean = _arg_1;
            var effectMC:MovieClip = _arg_2;
            var persistent:Boolean = _arg_3;
            doLoop = function ():void
            {
                if (effectMC.currentFrame >= (effectMC.totalFrames - 1))
                {
                    effectMC.gotoAndStop(1);
                };
            };
            var options:Object = {"hitStunPause":false};
            if (persistent)
            {
                options = {
                    "persistent":true,
                    "hitStunPause":false
                };
            }
            else
            {
                options = {
                    "persistent":false,
                    "hitStunPause":false
                };
            };
            if (looping)
            {
                this.createTimer(1, 0, doLoop, {"hitStunPause":false});
            }
            else
            {
                this.destroyTimer(doLoop);
            };
        }

        public function jumpToContinue(_arg_1:*=null):*
        {
            this.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.updateAttackStats({
                "allowControl":false,
                "cancelWhenAirborne":true
            });
            this.stancePlayFrame("continue");
        }


    }
}

