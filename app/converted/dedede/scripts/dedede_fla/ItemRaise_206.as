package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemRaise_206 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function ItemRaise_206()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 14, this.frame15, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame8():*
        {
            this.self.getItem().activateItem();
        }

        internal function frame15():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("dedede_bellySlap2");
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

