package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Stunned_227 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Stunned_227()
        {
            super();
            addFrameScript(0, this.frame1, 40, this.frame41);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("dedede_dizzy", true);
                };
            };
        }

        internal function frame41():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}

