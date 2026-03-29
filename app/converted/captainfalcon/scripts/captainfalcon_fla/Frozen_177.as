package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Frozen_177 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var self:CaptainExt;

        public function Frozen_177()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
                stop();
            };
        }


    }
}

