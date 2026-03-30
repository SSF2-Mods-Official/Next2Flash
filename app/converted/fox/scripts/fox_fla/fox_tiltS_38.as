package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_tiltS_38 extends MovieClip
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

        public function fox_tiltS_38()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame3():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}

