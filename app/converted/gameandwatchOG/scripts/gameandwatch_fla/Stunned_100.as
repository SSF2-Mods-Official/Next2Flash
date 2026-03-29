package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Stunned_100 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Stunned_100()
        {
            super();
            addFrameScript(0, this.frame1, 31, this.frame32);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame32():*
        {
            this.self.stancePlayFrame("hurt1");
        }


    }
}

