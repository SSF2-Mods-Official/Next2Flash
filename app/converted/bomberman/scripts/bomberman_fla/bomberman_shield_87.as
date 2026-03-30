package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_shield_87 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_shield_87()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame4():*
        {
            this.gotoAndStop("loop");
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }


    }
}

