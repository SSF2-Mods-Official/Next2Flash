package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_roll_tech_121 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_roll_tech_121()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.setGlobalVariable("canStartRise", true);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("fox_grunt2", true);
                };
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

