package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class TechRoll_96 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function TechRoll_96()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.setGlobalVariable("canStartRise", true);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("ssf2_snd_vfx_simon_attack02", true);
                };
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

