package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_jump_19 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var xframe:*;
        public var done:*;

        public function bomberman_jump_19()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.xframe = "midair";
            this.done = false;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.swapDepthsWithGrabbedOpponent(true);
                if (this.self.getGlobalVariable("screwAttackOn"))
                {
                    this.self.endAttack();
                    this.self.forceAttack("item_screw");
                };
            };
        }

        internal function frame2():*
        {
            this.self.playSound("bomberman_jump1");
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}

