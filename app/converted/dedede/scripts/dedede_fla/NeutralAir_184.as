package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class NeutralAir_184 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var playsound:Number;
        public var audio:Number;

        public function NeutralAir_184()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 5, this.frame6, 14, this.frame15, 18, this.frame19, 19, this.frame20, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_blast", {
                "scaleX":2.5,
                "scaleY":2.5,
                "y":-20,
                "parentLock":true
            });
            this.self.setLandingLag(true);
            this.self.playSound("ssf2_snd_sfx_dedede_nair");
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
                "damage":7,
                "direction":80,
                "power":50,
                "effectSound":"brawl_punch_m",
                "effect_id":"effect_hit3"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":7,
                "direction":80,
                "power":50,
                "effectSound":"brawl_punch_m",
                "effect_id":"effect_hit3"
            });
        }

        internal function frame15():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_landHeavy");
            };
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

