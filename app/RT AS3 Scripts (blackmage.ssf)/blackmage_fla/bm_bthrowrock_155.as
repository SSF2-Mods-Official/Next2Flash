// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.bm_bthrowrock_155

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class bm_bthrowrock_155 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var self:*;
        internal var character:*;
        internal var isOnGround:*;

        public function bm_bthrowrock_155()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 23, this.frame24);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:*;
            var _local_3:*;
            var _local_4:*;
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
            };
            this.visible = false;
            this.isOnGround = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character.setGlobalVariable("bthrowProjectileDied", false);
            };
        }

        internal function frame4():*
        {
            this.isOnGround = this.self.isOnGround();
            if (!this.isOnGround)
            {
                this.character.setGlobalVariable("bthrowProjectileDied", true);
                this.self.destroy();
            };
            this.visible = true;
        }

        internal function frame24():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

