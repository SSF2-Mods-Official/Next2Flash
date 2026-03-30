package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class BandanaDeeKirby_189 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var maxCharge:*;
        public var controls:*;

        public function BandanaDeeKirby_189()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 9, this.frame10, 10, this.frame11, 12, this.frame13, 14, this.frame15, 23, this.frame24, 28, this.frame29, 29, this.frame30, 35, this.frame36, 36, this.frame37, 38, this.frame39, 51, this.frame52, 61, this.frame62);
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
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.maxCharge = 15;
            this.controls = null;
            if (SSF2API.isReady() && this.self)
            {
                this.self.setupHatEffect(1, 11, -5);
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, 0, this.charging);
        }

        internal function frame10():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame11():*
        {
            this.self.setXSpeed(2, false);
            this.self.destroyTimer(this.charging);
            this.self.updateAttackStats({"allowControl":true});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
            this.self.setupHatEffect(2, 11, -5);
        }

        internal function frame13():*
        {
            this.self.playAttackSound(1);
            this.self.playSound("ssf2_snd_vfx_kirby_attack04");
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

        internal function frame29():*
        {
            if (this.self.isOnGround())
            {
                this.self.setXSpeed(-2, false);
            };
        }

        internal function frame30():*
        {
            if (this.self.getMetalStatus())
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
            this.self.updateAttackStats({"allowControl":true});
            this.self.setupHatEffect(3, 11, -5);
        }

        internal function frame39():*
        {
            this.self.fireProjectile("dee_nspec");
            this.self.setXSpeed(-6, false);
            this.self.playAttackSound(2);
            this.self.playSound("ssf2_snd_vfx_kirby_attack03");
        }

        internal function frame52():*
        {
            if (this.self.isOnGround())
            {
                this.self.setXSpeed(-5);
            };
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }


    }
}

