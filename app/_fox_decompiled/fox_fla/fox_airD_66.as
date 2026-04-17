package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_airD_66 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var playsound:Number;
        public var audio:Number;

        public function fox_airD_66()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6, 7, this.frame8, 9, this.frame10, 11, this.frame12, 13, this.frame14, 18, this.frame19, 26, this.frame27, 27, this.frame28, 32, this.frame33);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame4():*
        {
            this.self.addEffectToList(this.self.attachEffect("global_dust_spiral", {
                "x":this.self.flipX(10),
                "scaleY":1.2,
                "rotation":this.self.flipX(-20),
                "y":-15,
                "loop":2,
                "parentLock":true
            }));
            this.self.clearEffectsOnStateChange();
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
            this.self.playAttackSound(1);
        }

        internal function frame6():*
        {
            this.self.refreshAttackID();
            this.self.playAttackSound(1);
        }

        internal function frame8():*
        {
            this.self.refreshAttackID();
            this.self.playAttackSound(2);
        }

        internal function frame10():*
        {
            this.self.refreshAttackID();
            this.self.playAttackSound(2);
        }

        internal function frame12():*
        {
            this.self.refreshAttackID();
            this.self.playAttackSound(3);
        }

        internal function frame14():*
        {
            this.self.refreshAttackID();
            this.self.playAttackSound(3);
        }

        internal function frame19():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }

        internal function frame28():*
        {
            this.self.updateAttackStats({"cancelWhenAirborne":true});
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("fox_landLight");
            };
        }

        internal function frame33():*
        {
            this.self.endAttack();
        }


    }
}

