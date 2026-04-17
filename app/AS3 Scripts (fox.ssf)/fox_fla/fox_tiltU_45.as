// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_tiltU_45

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_tiltU_45 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var playsound:Number;
        public var audio:Number;

        public function fox_tiltU_45()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame4():*
        {
            if ((((this.playsound > 0.2) && (this.playsound <= 0.4)) && (!(this.audio == 1))))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((((this.playsound > 0.4) && (this.playsound <= 0.6)) && (!(this.audio == 2))))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((((this.playsound > 0.6) && (this.playsound <= 0.8)) && (!(this.audio == 3))))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((((this.playsound > 0.8) && (this.playsound <= 1)) && (!(this.audio == 4))))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

