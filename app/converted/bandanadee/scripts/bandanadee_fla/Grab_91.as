package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Grab_91 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:String;
        public var curSpeed:*;
        public var xDecay:*;
        public var xDecayPivot:*;
        public var isMovingRight:*;
        public var rand:int;

        public function Grab_91()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 16, this.frame17, 17, this.frame18, 21, this.frame22, 22, this.frame23, 24, this.frame25, 37, this.frame38, 38, this.frame39, 39, this.frame40, 40, this.frame41, 41, this.frame42, 42, this.frame43, 46, this.frame47);
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
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.xframe = "grab";
            if (this.self && SSF2API.isReady())
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.5));
            };
        }

        internal function frame3():*
        {
            SSF2API.playSound("grab_swing3");
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }

        internal function frame18():*
        {
            var _local_1:* = __activation__;
            this.xframe = "grab";
            this.curSpeed = this.self.getCharacterStat("max_xSpeed");
            this.xDecay = 0.7;
            this.xDecayPivot = 1;
            this.isMovingRight = (this.self.getXSpeed() > 0);
            this.self.createTimer(1, -1, this.xSpeedDecay);
            this.self.addEventListener(SSF2Event.CHAR_GRAB, function (_arg_1:*=null):*
            {
                self.destroyTimer(xSpeedDecay);
            });
        }

        internal function frame22():*
        {
            SSF2API.playSound("grab_swing5");
        }

        internal function frame23():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame25():*
        {
            this.self.destroyTimer(this.xSpeedDecay);
        }

        internal function frame38():*
        {
            this.self.endAttack();
        }

        internal function frame39():*
        {
            this.self.addEffectToList(this.self.attachEffect("grabbed_gfx", {
                "x":this.self.flipX(23),
                "y":-10,
                "scaleX":-0.4,
                "scaleY":-0.4
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame40():*
        {
            stop();
            this.xframe = "grab";
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

        internal function frame41():*
        {
            this.self.stancePlayFrame("grabbed2");
        }

        internal function frame42():*
        {
            this.xframe = "attack";
            this.self.refreshAttackID();
        }

        internal function frame43():*
        {
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_lightHit"});
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame47():*
        {
            this.self.stancePlayFrame("grabbed2");
        }


    }
}

