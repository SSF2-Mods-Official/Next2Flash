package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ForcePalm_109 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;
        public var xOffset:*;
        public var yOffset:*;
        public var xOffsetAir:*;
        public var yOffsetAir:*;
        public var character:*;

        public function ForcePalm_109()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8);
        }

        public function lock():void
        {
            if ((!(this.character.getCurrentAnimation()) == "b_forward") && (!(this.character.getCurrentAnimation()) == "b_forward_air"))
            {
                this.self.destroy();
            };
            if (this.character.isFacingRight())
            {
                if (this.character.isOnGround())
                {
                    this.self.setX((this.character.getX() + (this.xOffset * this.character.getScale().x)));
                }
                else
                {
                    this.self.setX((this.character.getX() + (this.xOffsetAir * this.character.getScale().x)));
                };
            }
            else if (this.character.isOnGround())
            {
                this.self.setX((this.character.getX() - (this.xOffset * this.character.getScale().x)));
            }
            else
            {
                this.self.setX((this.character.getX() - (this.xOffsetAir * this.character.getScale().x)));
            };
            if (this.character.isOnGround())
            {
                this.self.setY((this.character.getY() + (this.yOffset * this.character.getScale().y)));
            }
            else
            {
                this.self.setY((this.character.getY() + (this.yOffsetAir * this.character.getScale().y)));
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.xOffset = 44;
            this.yOffset = -23;
            this.xOffsetAir = 33.5;
            this.yOffsetAir = -28;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.self.createTimer(1, -1, this.lock);
                this.self.updateAttackBoxStats(1, {"damage":(this.self.getAttackBoxStat(1, "damage") * this.character.auraMultiplier)});
                if (this.character.isFacingRight())
                {
                    this.self.setScale(Math.pow((this.character.auraMultiplier + 0.33), 1.2), (0.74 + (this.character.auraMultiplier / 2.5)));
                }
                else
                {
                    this.self.setScale(-(Math.pow((this.character.auraMultiplier + 0.33), 1.2)), (0.74 + (this.character.auraMultiplier / 2.5)));
                };
            };
        }

        internal function frame8():*
        {
            this.self.destroy();
        }


    }
}

