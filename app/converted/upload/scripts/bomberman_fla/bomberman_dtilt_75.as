package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_dtilt_75 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_dtilt_75()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 4, this.frame5, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame3():*
        {
            this.self.setXSpeed(15, false);
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}

