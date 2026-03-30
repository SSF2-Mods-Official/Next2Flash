package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class DTilt_66 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var playsound:Number;
        public var audio:Number;

        public function DTilt_66()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame7():*
        {
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
            this.self.attachEffect("global_dust_light");
        }

        internal function frame8():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "hitStun":3,
                "selfHitStun":1,
                "direction":50,
                "power":65,
                "kbConstant":65,
                "onlyAffectsGround":false
            });
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

