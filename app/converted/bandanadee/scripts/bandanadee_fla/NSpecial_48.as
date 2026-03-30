package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class NSpecial_48 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var maxCharge:*;
        public var controls:*;

        public function NSpecial_48()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 9, this.frame10, 10, this.frame11, 12, this.frame13, 14, this.frame15, 23, this.frame24, 29, this.frame30, 35, this.frame36, 36, this.frame37, 38, this.frame39, 51, this.frame52, 61, this.frame62);
        }

        public function charging(_arg_1:*=null):*
        {
            this.controls = this.self.getControls();
            if (this.controls.BUTTON1)
            {
                this.maxCharge--;
                if (this.maxCharge <= 0)
                {
                    this.gotoAndPlay("FullCharge");
                };
            }
            else
            {
                this.gotoAndPlay("NoCharge");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.maxCharge = 15;
            this.controls = null;
            if (this.self && SSF2API.isReady())
            {
                if (!(this.self.isOnGround()) && (this.self.getYSpeed() > 0))
                {
                    this.self.setYSpeed(0);
                };
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, 0, this.charging);
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame11():*
        {
            this.self.destroyTimer(this.charging);
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":-1
            });
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"canFallOff":true});
                if ((this.self.isFacingRight() && (this.self.getXSpeed() < 2)) || (!(this.self.isFacingRight()) && (this.self.getXSpeed() > -2)))
                {
                    this.self.setXSpeed(2, false);
                };
            }
            else if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
        }

        internal function frame13():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame24():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":70,
                "direction":70
            });
            this.self.updateAttackStats({"refreshRate":-1});
            this.self.refreshAttackID();
        }

        internal function frame30():*
        {
            if (this.self.isOnGround() && this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }

        internal function frame37():*
        {
            this.self.setXSpeed(5, false);
            this.self.destroyTimer(this.charging);
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":-1
            });
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"canFallOff":true});
            }
            else if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
        }

        internal function frame39():*
        {
            this.self.fireProjectile("dee_nspec", 0, -24);
            this.self.setXSpeed(-6, false);
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
        }

        internal function frame52():*
        {
            if (this.self.isOnGround())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_s1");
                };
                this.self.setXSpeed(-5, false);
            };
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }


    }
}

