package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_airdodge_79 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_airdodge_79()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 15, this.frame16, 23, this.frame24);
        }

        public function dodgeLand(_arg_1:*=null):*
        {
            this.self.toLand();
            this.self.stancePlayFrame("dodgeland");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame2():*
        {
            this.self.setIntangibility(true);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.dodgeLand);
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

