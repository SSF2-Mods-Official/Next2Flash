package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_101 extends MovieClip
    {

        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Dizzy_101()
        {
            super();
            addFrameScript(0, this.frame1, 33, this.frame34);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame34():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

