package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_fall_21 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_fall_21()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame11():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

