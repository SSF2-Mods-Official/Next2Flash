package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_grab_48 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var touchBox:MovieClip;
        public var self:BombermanExt;
        public var xframe:String;
        public var curSpeed:*;
        public var xDecay:*;
        public var xDecayPivot:*;
        public var isMovingRight:*;
        public var rand:int;

        public function bomberman_grab_48()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 15, this.frame16, 16, this.frame17, 20, this.frame21, 21, this.frame22, 24, this.frame25, 36, this.frame37, 37, this.frame38, 38, this.frame39, 39, this.frame40, 40, this.frame41, 43, this.frame44, 47, this.frame48);
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
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.xframe = "grab";
            if (this.self && SSF2API.isReady())
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.6));
            };
        }

        internal function frame3():*
        {
            SSF2API.playSound("grab_swing4");
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
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
            this.xDecay = 0.6;
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
            SSF2API.playSound("grab_swing6");
        }

        internal function frame22():*
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

        internal function frame37():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            this.self.addEffectToList(this.self.attachEffect("grabbed_gfx", {
                "x":this.self.flipX(24),
                "y":-18,
                "scaleX":-0.4,
                "scaleY":-0.4
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame39():*
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

        internal function frame40():*
        {
            this.self.stancePlayFrame("grabbed2");
        }

        internal function frame41():*
        {
            this.xframe = "attack";
        }

        internal function frame44():*
        {
            this.self.updateAttackBoxStats(1, {"effect_id":"effect_lightHit"});
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-5)});
            this.self.refreshAttackID();
        }

        internal function frame48():*
        {
            this.self.stancePlayFrame("grabbed2");
        }


    }
}

