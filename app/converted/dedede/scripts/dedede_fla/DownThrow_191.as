package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class DownThrow_191 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var camBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var touchBox:MovieClip;
        public var self:DededeExt;
        public var playsound:Number;
        public var audio:Number;

        public function DownThrow_191()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 10, this.frame11, 12, this.frame13, 16, this.frame17, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame2():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame5():*
        {
            this.self.playSound("throw_woosh");
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame11():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame13():*
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
            this.self.forceGrabbedHurtFrame("downed");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-10),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame17():*
        {
            this.self.attachEffect("global_dust_cloud");
            SSF2API.getCamera().shake(4);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

