package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ForwardTilt_31 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var playsound:Number;
        public var audio:Number;

        public function ForwardTilt_31()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 5, this.frame6, 6, this.frame7, 7, this.frame8, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame2():*
        {
            this.self.fireProjectile("chibi_ftiltProj");
        }

        internal function frame4():*
        {
        }

        internal function frame6():*
        {
            this.self.playAttackSound(1);
            this.self.setXSpeed(10, false);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame7():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            };
        }

        internal function frame8():*
        {
            this.self.updateAttackStats({"refreshRate":90});
            this.self.updateAttackBoxStats(1, {
                "damage":5,
                "power":32,
                "shock":true,
                "hitLag":-1,
                "effectSound":"brawl_zap_m"
            });
            this.self.refreshAttackID();
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

