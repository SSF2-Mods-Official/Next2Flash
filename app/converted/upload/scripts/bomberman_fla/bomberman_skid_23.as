package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_skid_23 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_skid_23()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame4():*
        {
            this.self.endAttack();
        }


    }
}

