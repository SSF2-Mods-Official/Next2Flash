package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_23 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Helpless_23()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("redo");
            };
        }

        internal function frame8():*
        {
            this.self.stancePlayFrame("redo");
        }


    }
}

