package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_77 extends MovieClip
    {

        public var hand:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function Helpless_77()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame8():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

