package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class SSpecial_53 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var proj:*;
        public var land:*;

        public function SSpecial_53()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 11, this.frame12, 23, this.frame24, 27, this.frame28, 44, this.frame45);
        }

        public function toLand(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
            this.land = true;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.proj = null;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.land = this.self.isOnGround();
                if (!this.land)
                {
                    this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
                };
                this.self.killSpear();
                if (this.self.spearObj && !(this.self.spearObj.isDisposed()) && !(this.self.spearObj.inState(PState.DEAD)))
                {
                    this.self.stancePlayFrame("fail");
                };
            };
        }

        internal function frame11():*
        {
            if (this.self.getMetalStatus() && this.self.isOnGround())
            {
                this.self.playSound("metal_step_s2");
            };
        }

        internal function frame12():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            if (this.land)
            {
                this.proj = this.self.fireProjectile("dee_spear", 3, -10);
                if (this.proj)
                {
                    this.proj.setYSpeed(-9);
                    this.proj.setXSpeed(12, false);
                };
            }
            else
            {
                this.self.fireProjectile("dee_spear", 12, 0);
            };
        }

        internal function frame24():*
        {
            if (!this.land)
            {
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            };
        }

        internal function frame28():*
        {
            this.self.endAttack();
        }

        internal function frame45():*
        {
            this.self.endAttack();
        }


    }
}

