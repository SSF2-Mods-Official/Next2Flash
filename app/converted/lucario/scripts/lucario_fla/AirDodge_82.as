package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class AirDodge_82 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function AirDodge_82()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 13, this.frame14, 15, this.frame16, 21, this.frame22);
        }

        public function dodgeLand(_arg_1:*=null):*
        {
            this.self.toLand();
            this.self.stancePlayFrame("dodgeland");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.dodgeLand);
        }

        internal function frame4():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame14():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame16():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }


    }
}

