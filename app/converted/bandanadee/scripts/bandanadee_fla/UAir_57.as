package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class UAir_57 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var playsound:Number;
        public var audio:Number;

        public function UAir_57()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 5, this.frame6, 14, this.frame15, 19, this.frame20, 20, this.frame21, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (this.self && SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
        }

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "power":30,
                "effectSound":"sw_brawl_hit_M"
            });
        }

        internal function frame15():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }

        internal function frame21():*
        {
            this.self.attachEffect("effect_bdee_land", {"y":-15});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("bandanadee_land1");
            };
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

