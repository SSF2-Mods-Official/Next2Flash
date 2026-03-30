package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Grab_144 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;
        public var curSpeed:*;
        public var xDecay:*;
        public var xDecayPivot:*;
        public var isMovingRight:*;
        public var rand:int;

        public function Grab_144()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 15, this.frame16, 16, this.frame17, 20, this.frame21, 21, this.frame22, 26, this.frame27, 36, this.frame37, 37, this.frame38, 38, this.frame39, 39, this.frame40, 40, this.frame41, 41, this.frame42, 42, this.frame43, 46, this.frame47);
        }

        public function xSpeedDecay():void
        {
            if ((this.self.getXSpeed() == 0) || (this.isMovingRight != (this.self.getXSpeed() > 0)))
            {
                this.self.setXSpeed(0);
                this.self.destroyTimer(this.xSpeedDecay);
                return;
            };
            this.curSpeed -= ((this.isMovingRight == this.self.isFacingRight()) ? this.xDecay : this.xDecayPivot);
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
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = "grab";
            if (this.self && SSF2API.isReady())
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.9));
            };
        }

        internal function frame3():*
        {
            SSF2API.playSound("grab_swing2");
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-12)});
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            var _local_1:* = __activation__;
            this.xframe = "grab";
            this.curSpeed = this.self.getCharacterStat("max_xSpeed");
            this.xDecay = 0.5;
            this.xDecayPivot = 0.9;
            this.isMovingRight = (this.self.getXSpeed() > 0);
            this.self.createTimer(1, -1, this.xSpeedDecay);
            this.self.addEventListener(SSF2Event.CHAR_GRAB, function (_arg_1:*=null):*
            {
                self.destroyTimer(xSpeedDecay);
            });
        }

        internal function frame21():*
        {
            SSF2API.playSound("grab_swing4");
        }

        internal function frame22():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-1),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame27():*
        {
            this.self.destroyTimer(this.xSpeedDecay);
        }

        internal function frame37():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.addEffectToList(this.self.attachEffect("grabbed_gfx", {
                "x":this.self.flipX(40),
                "y":-16,
                "scaleX":-0.4,
                "scaleY":-0.4
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame39():*
        {
            this.xframe = "grab";
            stop();
            this.rand = 0;
            if (this.self.isCPU() && (this.self.getCPULevel() >= 1))
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 6)
                {
                    this.self.stancePlayFrame("attack");
                };
            };
        }

        internal function frame40():*
        {
            gotoAndStop("grabbed2");
        }

        internal function frame41():*
        {
            this.xframe = "attack";
        }

        internal function frame42():*
        {
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_lightHit"});
            this.self.refreshAttackID();
        }

        internal function frame43():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-12)});
        }

        internal function frame47():*
        {
            this.gotoAndStop("grabbed2");
        }


    }
}

