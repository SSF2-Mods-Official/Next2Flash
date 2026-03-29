package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_44 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Helpless_44()
        {
            super();
            addFrameScript(0, this.frame1, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady() && this.self)
            {
                if (this.self.getGlobalVariable("usedSpec"))
                {
                    this.self.setGlobalVariable("usedSpec", false);
                    this.self.stancePlayFrame("spec");
                }
                else
                {
                    this.self.stancePlayFrame("reg");
                };
            };
        }

        internal function frame15():*
        {
            this.self.stancePlayFrame("spec");
        }


    }
}

