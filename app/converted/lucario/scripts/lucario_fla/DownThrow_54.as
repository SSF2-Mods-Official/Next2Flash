package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class DownThrow_54 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var touchBox:MovieClip;
        public var self:LucarioExt;
        public var playsound:Number;
        public var audio:Number;

        public function DownThrow_54()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.updateAuraDamage([1]);
                this.self.updateAuraPaws();
            };
        }

        internal function frame11():*
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
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.75,
                "scaleY":0.75
            });
            this.self.attachEffect("ground_bounce", {
                "scaleX":0.75,
                "scaleY":0.75
            });
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

