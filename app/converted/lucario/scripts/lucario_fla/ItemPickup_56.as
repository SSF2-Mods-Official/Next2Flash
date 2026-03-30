package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemPickup_56 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function ItemPickup_56()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame2():*
        {
            this.self.pickupItem();
            this.self.attachEffect("itempickup_effect", {
                "x":this.self.flipX(11),
                "y":-1
            });
        }

        internal function frame5():*
        {
            this.self.endAttack();
        }


    }
}

