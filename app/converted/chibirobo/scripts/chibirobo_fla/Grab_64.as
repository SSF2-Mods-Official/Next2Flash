package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Grab_64 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:ChibiExt;
        public var xframe:String;
        public var pummeled:Boolean;
        public var dir:*;
        public var curSpeed:*;
        public var xDecay:*;
        public var isMovingRight:*;

        public function Grab_64()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 8, this.frame9, 34, this.frame35, 61, this.frame62, 88, this.frame89, 89, this.frame90, 98, this.frame99, 99, this.frame100, 127, this.frame128, 156, this.frame157, 185, this.frame186, 186, this.frame187, 190, this.frame191, 191, this.frame192, 195, this.frame196, 196, this.frame197, 200, this.frame201, 201, this.frame202, 202, this.frame203, 203, this.frame204, 204, this.frame205, 206, this.frame207, 213, this.frame214);
        }

        public function xSpeedDecay():void
        {
            if ((this.self.getXSpeed() == 0) || (this.isMovingRight != (this.self.getXSpeed() > 0)))
            {
                this.self.setXSpeed(0);
                this.self.destroyTimer(this.xSpeedDecay);
                return;
            };
            this.curSpeed -= this.xDecay;
            if (this.curSpeed > 0)
            {
                this.self.setXSpeed(((this.isMovingRight) ? this.curSpeed : -(this.curSpeed)));
            }
            else
            {
                this.self.setXSpeed(0);
                this.self.destroyTimer(this.xSpeedDecay);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.xframe = "grab";
            this.pummeled = false;
            this.dir = "forward";
            if (this.self && SSF2API.isReady())
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.6));
            };
        }

        internal function frame8():*
        {
            SSF2API.playSound("grab_swing4");
        }

        internal function frame9():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
            if (this.self.getControls().UP)
            {
                this.dir = "up";
                this.self.stancePlayFrame("up");
            }
            else if (this.self.getControls().DOWN)
            {
                this.dir = "down";
                this.self.stancePlayFrame("down");
            };
        }

        internal function frame35():*
        {
            this.self.endAttack();
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }

        internal function frame89():*
        {
            this.self.endAttack();
        }

        internal function frame90():*
        {
            var _local_1:* = __activation__;
            this.xframe = "grab";
            this.curSpeed = this.self.getCharacterStat("max_xSpeed");
            this.xDecay = 0.5;
            this.isMovingRight = (this.self.getXSpeed() > 0);
            this.self.createTimer(1, -1, this.xSpeedDecay);
            this.self.addEventListener(SSF2Event.CHAR_GRAB, function (_arg_1:*=null):*
            {
                self.destroyTimer(xSpeedDecay);
            });
        }

        internal function frame99():*
        {
            SSF2API.playSound("grab_swing6");
        }

        internal function frame100():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            this.self.destroyTimer(this.xSpeedDecay);
            if (this.self.getControls().UP)
            {
                this.dir = "up";
                this.self.stancePlayFrame("dash_up");
            }
            else if (this.self.getControls().DOWN)
            {
                this.dir = "down";
                this.self.stancePlayFrame("dash_down");
            };
        }

        internal function frame128():*
        {
            this.self.endAttack();
        }

        internal function frame157():*
        {
            this.self.endAttack();
        }

        internal function frame186():*
        {
            this.self.endAttack();
        }

        internal function frame187():*
        {
            this.xframe = "grab";
            if (this.dir != "forward")
            {
                this.gotoAndStop(("grabbed" + this.dir));
            };
            if (this.pummeled)
            {
                this.gotoAndStop("loop");
            };
        }

        internal function frame191():*
        {
            this.gotoAndStop("loop_start");
        }

        internal function frame192():*
        {
            this.dir = "forward";
            if (this.pummeled)
            {
                this.gotoAndStop("loop");
            };
        }

        internal function frame196():*
        {
            this.gotoAndStop("loop_start");
        }

        internal function frame197():*
        {
            this.dir = "forward";
        }

        internal function frame201():*
        {
            this.gotoAndStop("loop_start");
        }

        internal function frame202():*
        {
            this.self.addEffectToList(this.self.attachEffect("grabbed_gfx", {
                "x":this.self.flipX(19),
                "y":-21,
                "scaleX":-0.4,
                "scaleY":-0.4
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame203():*
        {
            this.xframe = "grab";
            this.self.swapDepthsWithGrabbedOpponent(false);
            stop();
        }

        internal function frame204():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame205():*
        {
            this.xframe = "attack";
            this.pummeled = true;
        }

        internal function frame207():*
        {
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_lightHit"});
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-4)});
        }

        internal function frame214():*
        {
            this.gotoAndStop("loop");
        }


    }
}

