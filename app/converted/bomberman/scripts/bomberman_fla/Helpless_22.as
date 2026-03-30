package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_22 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function Helpless_22()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame9():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

