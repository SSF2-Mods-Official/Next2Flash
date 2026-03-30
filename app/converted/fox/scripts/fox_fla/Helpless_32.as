package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_32 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function Helpless_32()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (SSF2API.isReady() && this.self)
            {
                if (this.self.getGlobalVariable("usedUpB"))
                {
                    this.self.setGlobalVariable("usedUpB", false);
                    this.self.stancePlayFrame("up");
                }
                else
                {
                    this.self.stancePlayFrame("reg");
                };
            };
        }

        internal function frame11():*
        {
            this.self.stancePlayFrame("up");
        }


    }
}

